import ast
import datetime
import logging
from csv import DictWriter
from dataclasses import dataclass
from typing import List, Optional, Tuple

import requests
from langchain.chat_models import ChatOpenAI
from langchain.retrievers.weaviate_hybrid_search import WeaviateHybridSearchRetriever

from codinit.agents import (
    code_correcting_agent,
    coding_agent,
    dependency_agent,
    planner_agent,
)
from codinit.code_editor import PythonCodeEditor
from codinit.config import client, eval_settings

# from codinit.get_context import get_embedding_store, get_read_the_docs_context
from codinit.get_context_ import get_relevant_documents, get_retriever
from codinit.queries import get_classes, get_files, get_functions, get_imports

logger = logging.getLogger(__name__)
ANSWER_PATTERN = r"[a-zA-Z]+"
DEPENDENCY_BLACKLIST = set(["random", "json"])


def _trim_md(code_editor: PythonCodeEditor):
    if code_editor.source_code:
        code_editor.source_code[0] = code_editor.source_code[0].replace("```python", "")
        code_editor.source_code[-1] = code_editor.source_code[-1].replace("```", "")
        code_editor.overwrite_code(code_editor.display_code())


# TODO: Check difference between dataclass and pydantic object: https://towardsdatascience.com/pydantic-or-dataclasses-why-not-both-convert-between-them-ba382f0f9a9c
@dataclass
class TaskExecutionConfig:
    execute_code = True
    install_dependencies = True
    check_package_is_in_pypi = True
    log_to_stdout = True
    coding_attempts = 1
    max_coding_attempts = 5
    dependency_install_attempts = 5
    planner_temperature = 0
    coder_temperature = 0.0
    code_corrector_temperature = 0
    dependency_tracker_temperature = 0


class TaskExecutor:
    def __init__(
        self,
        code_editor: PythonCodeEditor,
        config: TaskExecutionConfig,
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

    def install_dependencies(self, deps: List[str]) -> str:
        # if it's a string, e.g. "['openai']", turn into list ['openai']
        if isinstance(deps, str):
            try:
                deps = ast.literal_eval(deps)
            except (SyntaxError, ValueError):
                print("The string couldn't be evaluated.")
        # print(type(deps))
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

    def get_docs(self, task: str):
        # first get context from provided libraries
        retriever = WeaviateHybridSearchRetriever(
            client=client,
            index_name="DocumentionFile",
            text_key="content",
            k=10,
            alpha=0.75,
        )
        relevant_docs = get_relevant_documents(query=task, retriever=retriever)
        return relevant_docs

    def execute(
        self,
        task: str,
        libraries: Optional[List[str]] = None,
        source_code: Optional[str] = None,
    ):
        # Generating a coding plan
        retriever = WeaviateHybridSearchRetriever(
            client=client,
            index_name="DocumentionFile",
            text_key="content",
            k=10,
            alpha=0.75,
        )

        relevant_docs = get_relevant_documents(query=task, retriever=retriever)
        # get_embedding_store(start_urls=libraries)
        # relevant_docs = get_read_the_docs_context(task, k=10)
        # generate coding plan given context
        plan = self.planner.execute(
            function_name="execute_plan", task=task, context=relevant_docs
        )

        # install dependencies from plan
        if self.config.execute_code and self.config.install_dependencies:
            deps = self.dependency_tracker.execute(
                function_name="install_dependencies", plan=plan
            )
            self.install_dependencies(deps)

        # generate code
        new_code = self.coder.execute(
            task=task,
            function_name="execute_code",
            source_code=self.code_editor.display_code(),
            plan=plan,
            context=relevant_docs,
        )
        new_code = self.format_code(code=new_code, dependencies=deps)
        self.code_editor.overwrite_code(new_source=new_code)
        validation = (
            self.code_editor.run_linter()
        )  # validate_code_imports(code=new_code, dependencies = deps)
        print(f"{validation=}")
        # run generated code
        error = self.run_code(new_code)

        attempt = 0
        while "Failed" in error:
            if attempt > self.config.coding_attempts:
                break
            # corrected code
            new_code = self.code_corrector.execute(
                function_name="execute_code",
                task=task,
                context=relevant_docs,
                source_code=new_code,
                error=error,
            )
            new_code = self.format_code(code=new_code, dependencies=deps)
            self.code_editor.overwrite_code(new_source=new_code)
            validation = (
                self.code_editor.run_linter()
            )  # validate_code_imports(code=new_code, dependencies = deps)
            print(f"{validation=}")
            error = self.run_code(new_code)
            attempt += 1
        return new_code

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

    # TODO: add plan to benchmark
    def execute_and_log(
        self,
        task: str,
        run_id: int,
        task_id: int,
        sha: str,
        message: str,
        csv_writer: DictWriter,
        libraries: Optional[List[str]] = None,
        source_code: Optional[str] = None,
    ):
        attempt = 0
        chat_history = []
        # Generating a coding plan
        retriever = WeaviateHybridSearchRetriever(
            client=client,
            index_name="DocumentionFile",
            text_key="content",
            k=10,
            alpha=0.75,
        )
        time_stamp = datetime.datetime.now().isoformat()
        relevant_docs = get_relevant_documents(query=task, retriever=retriever)
        # get_embedding_store(start_urls=libraries)
        # relevant_docs = get_read_the_docs_context(task, k=10)
        # generate coding plan given context
        plan = self.planner.execute(
            function_name="execute_plan",
            chat_history=[],
            task=task,
            context=relevant_docs,
        )

        # install dependencies from plan
        if self.config.execute_code and self.config.install_dependencies:
            deps = self.dependency_tracker.execute(
                function_name="install_dependencies", chat_history=[], plan=plan
            )
            self.install_dependencies(deps)
        chat_history.append(
            {"role": "user", "content": f"installed dependencies {deps}"}
        )
        # generate code
        new_code = self.coder.execute(
            task=task,
            function_name="execute_code",
            chat_history=chat_history,
            plan=plan,
            context=relevant_docs,
        )
        new_code = self.format_code(code=new_code, dependencies=deps)
        formatted_code, lint_result, metric = self.format_lint_code(
            code=new_code, dependencies=deps
        )
        # feed in lint results
        print(f"{lint_result=}")
        new_code = self.code_corrector.execute(
            function_name="execute_code",
            chat_history=[],
            task=task,
            context=relevant_docs,
            source_code=new_code,
            error=lint_result,
        )
        formatted_code, lint_result, metric = self.format_lint_code(
            code=new_code, dependencies=deps
        )
        # run generated code
        error = self.run_code(formatted_code)
        # file has header: Run_ID,Task_ID,Task,Generation_ID,Code,Linter_Output,Metric,Error_Log,Git_SHA,Commit_Message,Timestamp
        row = [
            run_id,
            task_id,
            task,
            attempt,
            formatted_code,
            lint_result,
            metric,
            error,
            sha,
            message,
            time_stamp,
        ]
        row_dict = {
            key: value for key, value in list(zip(eval_settings.eval_columns, row))
        }
        csv_writer.writerow(row_dict)
        attempt = 1
        while "Failed" in error:
            if attempt > self.config.coding_attempts:
                break
            time_stamp = datetime.datetime.now().isoformat()
            # corrected code
            new_code = self.code_corrector.execute(
                function_name="execute_code",
                task=task,
                context=relevant_docs,
                source_code=new_code,
                error=error,
            )
            formatted_code, lint_result, metric = self.format_lint_code(
                code=new_code, dependencies=deps
            )
            # run generated code
            error = self.run_code(formatted_code)
            # file has header: Run_ID,Task_ID,Task,Generation_ID,Code,Linter_Output,Metric,Error_Log,Git_SHA,Commit_Message,Timestamp
            row = [
                run_id,
                task_id,
                task,
                attempt,
                formatted_code,
                lint_result,
                metric,
                error,
                sha,
                message,
                time_stamp,
            ]
            row_dict = {
                key: value for key, value in list(zip(eval_settings.eval_columns, row))
            }
            csv_writer.writerow(row_dict)
            attempt += 1
        return new_code
