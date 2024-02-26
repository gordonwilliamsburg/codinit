import ast
import logging
from csv import DictWriter
from datetime import datetime
from typing import List, Optional, Tuple, Union

import openai
import requests
import weaviate
from apify_client import ApifyClient
from pydantic import BaseModel

from codinit.agents import (
    code_correcting_agent,
    coding_agent,
    dependency_agent,
    linting_agent,
    planner_agent,
)
from codinit.code_editor import PythonCodeEditor
from codinit.codebaseKG import run_codebase_analysis
from codinit.config import eval_settings, secrets

# from codinit.get_context import get_embedding_store, get_read_the_docs_context
from codinit.documentation.get_context import WeaviateDocLoader, WeaviateDocQuerier
from codinit.documentation.pydantic_models import Library
from codinit.documentation.save_document import ScraperSaver
from codinit.experiment_tracking.experiment_logger import ExperimentLogger
from codinit.experiment_tracking.experiment_pydantic_models import (
    CodeGeneration,
    CorrectionLoop,
    Dependencies,
    DocumentationScraping,
    GeneratedPlan,
    InitialCode,
    LintingAttempt,
    TaskExecutionConfig,
)
from codinit.weaviate_client import get_weaviate_client

logger = logging.getLogger(__name__)
ANSWER_PATTERN = r"[a-zA-Z]+"
DEPENDENCY_BLACKLIST = set(["random", "json"])


def _trim_md(code_editor: PythonCodeEditor):
    if code_editor.source_code:
        code_editor.source_code[0] = code_editor.source_code[0].replace("```python", "")
        code_editor.source_code[-1] = code_editor.source_code[-1].replace("```", "")
        code_editor.overwrite_code(code_editor.display_code())


class TaskExecutor:
    def __init__(
        self,
        code_editor: PythonCodeEditor,
        config: TaskExecutionConfig,
        task: str,
        run_id: int,
        task_id: int,
        sha: str,
        message: str,
        csv_writer: DictWriter,
    ) -> None:
        self.code_editor = code_editor
        self.config = config

        # Planner
        self.planner = planner_agent

        # Coder
        self.coder = coding_agent

        # Dependency tracker
        self.dependency_tracker = dependency_agent

        # Code corrector
        self.code_corrector = code_correcting_agent

        # linter
        self.linter = linting_agent

        self.task = task
        self.run_id = run_id
        self.task_id = task_id
        self.sha = (sha,)
        self.message = (message,)
        self.csv_writer = csv_writer
        self.experiment_logger: ExperimentLogger = ExperimentLogger(task_id=task_id)

    def install_dependencies(self, deps: List[str]) -> str:
        # if it's a string, e.g. "['openai']", turn into list ['openai']
        if isinstance(deps, str):
            try:
                deps = ast.literal_eval(deps)
            except (SyntaxError, ValueError):
                logging.error("The string couldn't be evaluated.")
        dependencies = []
        for d in deps:
            d = d.strip()
            if " " in d:
                d = d.split(" ")[0]

            if self.config.check_package_is_in_pypi:
                url = f"https://pypi.org/project/{d}"
                res = requests.get(url)
                if res.status_code != 200:
                    pass

            if len(d) < 2 or d in DEPENDENCY_BLACKLIST:
                continue

            dependencies.append(d)

        if dependencies:
            dependencies = list(set(dependencies))
            dependencies += ["langchain", "pydantic", "openai", "wikipedia"]
            logger.info(f"{dependencies=}")

            for dependency in dependencies:
                self.code_editor.add_dependency(dependency)

            self.code_editor.create_env()
            process = self.code_editor.install_dependencies()
            if process.returncode != 0:
                logger.error(f"Dependency install failed for: {dependencies}")

            message = f"dependency installer results: args={process.args}, return_code=stdout={process.stdout}, stderr={process.stderr}, return_code={process.returncode}"
        else:
            message = "no dependencies to install."
        return message

    def run_code(self, code: str) -> str:
        self.code_editor.overwrite_code(code)
        _trim_md(self.code_editor)
        self.code_editor.save_code()
        logger.info(self.code_editor.display_code())

        if not self.config.execute_code:
            return self.code_editor.display_code()

        result = self.code_editor.run_code()

        if "Succeeded" in result:
            logger.info("Source code is functional!")
            return "Task Success: " + result
        else:
            logger.info("Failed to generate an executable source code.")
            return "Task Failed: " + result

    def format_code(self, code: str, dependencies: List[str]) -> str:
        formatted_code = code
        for dep in dependencies:
            formatted_code = self.code_editor.process_imports(
                code=formatted_code, library_name=dep
            )
        return formatted_code

    """
    def get_docs_old(self, libraries: List[str], task: str):
        # first get context from provided libraries
        get_embedding_store(start_urls=libraries)
        relevant_docs = get_read_the_docs_context(task, k=5)
        return relevant_docs
    """

    def scrape_docs(self, library: Library):
        client = ApifyClient(secrets.apify_key)
        scraper_saver = ScraperSaver(libname=library.libname, apify_client=client)
        scraper_saver.scrape_and_save_apify_docs(urls=library.links)

    def init_library(self, library: Library, client: weaviate.Client):
        weaviate_doc_loader = WeaviateDocLoader(library=library, client=client)
        weaviate_doc_loader.run()
        run_codebase_analysis(
            repo_dir=secrets.repo_dir,
            libname=library.libname,
            repo_url=library.lib_repo_url,
            client=client,
        )

    def get_docs(self, library: Library, task: str, client: weaviate.Client):
        self.scrape_docs(library=library)
        self.init_library(library=library, client=client)
        weaviate_doc_querier = WeaviateDocQuerier(library=library, client=client)
        docs = weaviate_doc_querier.get_relevant_documents(query=task)
        logger.info(f"relevant_docs: {docs}")
        return docs

    def initial_code_generation(
        self, library: Library, client: weaviate.WeaviateClient
    ) -> InitialCode:
        chat_history = []
        # Generating a coding plan
        time_stamp = datetime.now()
        relevant_docs = self.get_docs(library=library, task=self.task, client=client)

        # generate coding plan given context
        plan = self.planner.execute(
            tool_choice="execute_plan",
            chat_history=[],
            task=self.task,
            context=relevant_docs,
        )[0]
        # install dependencies from plan
        if self.config.execute_code and self.config.install_dependencies:
            deps = self.dependency_tracker.execute(
                tool_choice="install_dependencies", chat_history=[], plan=plan
            )[0]
            self.install_dependencies(deps)
        chat_history.append(
            {"role": "assistant", "content": f"installed dependencies {deps}"}
        )
        # generate code
        # TODO grab thought from code execution function
        new_code = self.coder.execute(
            task=self.task,
            tool_choice="execute_code",
            chat_history=chat_history,
            plan=plan,
            context=relevant_docs,
        )[0]
        initial_code = InitialCode(
            Timestamp=time_stamp,
            Documentation_Scraping=DocumentationScraping(
                Relevant_Docs=relevant_docs, num_tokens=len(relevant_docs)
            ),
            Generated_Plan=GeneratedPlan(Plan=plan),
            Dependencies=Dependencies(Dependencies=deps),
            Coding_Agent=CodeGeneration(Generated_Code=new_code, Thought=""),
        )
        return initial_code

    def format_lint_code(
        self, code: str, dependencies: List[str]
    ) -> Tuple[str, List[str], int]:
        formatted_code = self.format_code(code=code, dependencies=dependencies)
        self.code_editor.overwrite_code(new_source=formatted_code)
        lint_result = (
            self.code_editor.run_linter()
        )  # validate_code_imports(code=new_code, dependencies = deps)
        metric = len(lint_result)
        # run generated code
        return formatted_code, lint_result, metric

    def write_row(
        self,
        attempt: int,
        formatted_code: str,
        lint_result: List[str],
        metric: int,
        error: Union[str, List[str]],
        time_stamp: datetime,
    ):
        row = [
            self.run_id,
            self.task_id,
            self.task,
            attempt,
            formatted_code,
            lint_result,
            metric,
            error,
            self.sha,
            self.message,
            time_stamp,
        ]
        row_dict = {
            key: value for key, value in list(zip(eval_settings.eval_columns, row))
        }
        self.csv_writer.writerow(row_dict)

    def lint_and_correct_with_llm(
        self,
        new_code: str,
        relevant_docs: str,
        deps: List[str],
    ):
        time_stamp = datetime.now()
        lint_attempt = 0
        formatted_code, lint_result, metric = self.format_lint_code(
            code=new_code, dependencies=deps
        )
        self.write_row(
            attempt=lint_attempt,
            formatted_code=formatted_code,
            lint_result=lint_result,
            metric=metric,
            error="no runtime",
            time_stamp=time_stamp,
        )
        self.experiment_logger.init_lint_attempt_logs()
        linting_attempt = LintingAttempt(
            Timestamp=time_stamp,
            lint_attempt=lint_attempt,
            Code=formatted_code,
            Lint_Result=lint_result,
            Metric=metric,
        )
        self.experiment_logger.log_linting_attempt(linting_attempt=linting_attempt)
        logging.info(f"{lint_result=}")
        while (
            len(lint_result) > 0
            and lint_attempt < self.config.lint_correction_threshold
        ):
            time_stamp = datetime.now()
            lint_query_results = self.linter.execute(
                source_code=formatted_code, linter_output=lint_result
            )
            old_code = formatted_code
            logging.info(f"{lint_query_results=}")
            lint_response = (
                openai.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    messages=self.linter.messages,
                )
                .choices[0]
                .message
            )
            logging.info(f"{lint_response=}")
            # TODO extract thought from code execution function
            new_code = self.code_corrector.execute(
                tool_choice="execute_code",
                chat_history=[],
                task=self.task,
                context=relevant_docs,
                source_code=formatted_code,
                error=lint_response,
            )[0]
            lint_attempt += 1
            formatted_code, lint_result, metric = self.format_lint_code(
                code=new_code, dependencies=deps
            )
            linting_attempt = LintingAttempt(
                Timestamp=time_stamp,
                lint_attempt=lint_attempt,
                Code=old_code,
                Lint_Query_Result=lint_query_results,
                Lint_Response=lint_response,
                Generated_Code=CodeGeneration(
                    Thought="", Generated_Code=formatted_code
                ),
                Lint_Result=lint_result,
                Metric=metric,
            )
            self.experiment_logger.log_linting_attempt(linting_attempt=linting_attempt)
            logging.info(f"{lint_result=}")
            self.write_row(
                attempt=lint_attempt,
                formatted_code=formatted_code,
                lint_result=lint_result,
                metric=metric,
                error="no runtime",
                time_stamp=time_stamp,
            )
        return formatted_code

    def runtime_and_correct_with_llm(
        self,
        new_code: str,
        relevant_docs: str,
        attempt: int,
        deps: List[str],
    ):
        self.experiment_logger.init_correction_loop_logs()
        time_stamp = datetime.now()
        # run generated code and correct resulting error
        error1 = self.run_code(new_code)
        new_code = self.code_corrector.execute(
            tool_choice="execute_code",
            chat_history=[],
            task=self.task,
            context=relevant_docs,
            source_code=new_code,
            error=error1,
        )[0]
        formatted_code, lint_result, metric = self.format_lint_code(
            code=new_code, dependencies=deps
        )
        error2 = self.run_code(new_code)
        correction_loop = CorrectionLoop(
            Timestamp=time_stamp,
            Error1=error1,
            Generated_Code=CodeGeneration(Thought="", Generated_Code=formatted_code),
            Lint_Result=lint_result,
            Error2=error2,
            Metric=metric,
        )
        self.experiment_logger.log_correction_loop(correction_loop=correction_loop)
        self.write_row(
            attempt=attempt,
            formatted_code=formatted_code,
            lint_result=lint_result,
            metric=metric,
            error=error2,
            time_stamp=time_stamp,
        )
        return error2, new_code

    def code_correction_with_linting(
        self,
        new_code: str,
        deps: List[str],
        relevant_docs: str,
        attempt: int,
    ):
        time_stamp = datetime.now()
        # lint code and correct linting errors in a loop
        linted_code = self.lint_and_correct_with_llm(
            new_code=new_code,
            relevant_docs=relevant_docs,
            deps=deps,
        )
        # run generated code and correct resulting error
        error, new_code = self.runtime_and_correct_with_llm(
            new_code=linted_code,
            relevant_docs=relevant_docs,
            attempt=attempt,
            deps=deps,
        )
        end_time_stamp = datetime.now()
        time = (end_time_stamp - time_stamp).total_seconds()
        self.experiment_logger.log_self_healing_block(time=time, generation_id=attempt)
        return error, new_code

    # TODO: add plan to benchmark
    def execute_and_log(
        self,
        library: Library,
        source_code: Optional[str] = None,
    ):
        client = get_weaviate_client()
        attempt = 0
        initial_code_generation = self.initial_code_generation(
            library=library, client=client
        )
        self.experiment_logger.log_initial_code(initial_code=initial_code_generation)
        error, new_code = self.code_correction_with_linting(
            new_code=initial_code_generation.Coding_Agent.Generated_Code,
            deps=initial_code_generation.Dependencies.Dependencies,
            relevant_docs=initial_code_generation.Documentation_Scraping.Relevant_Docs,
            attempt=attempt,
        )
        attempt = 1
        while "Failed" in error:
            if attempt > self.config.coding_attempts:
                break
            # corrected code
            error, new_code = self.code_correction_with_linting(
                new_code=new_code,
                deps=initial_code_generation.Dependencies.Dependencies,
                relevant_docs=initial_code_generation.Documentation_Scraping.Relevant_Docs,
                attempt=attempt,
            )
            attempt += 1
        return new_code
