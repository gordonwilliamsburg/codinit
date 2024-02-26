from datetime import datetime
from typing import List, Optional, Tuple

from pydantic import BaseModel


class TaskExecutionConfig(BaseModel):
    execute_code: bool = True
    install_dependencies: bool = True
    check_package_is_in_pypi: bool = True
    log_to_stdout: bool = True
    coding_attempts: int = 1
    max_coding_attempts: int = 5
    dependency_install_attempts: int = 5
    planner_temperature: float = 0
    coder_temperature: float = 0.0
    code_corrector_temperature: float = 0
    dependency_tracker_temperature: float = 0
    lint_correction_threshold: int = 3


class DocumentationScraping(BaseModel):
    Relevant_Docs: str
    num_tokens: int


class GeneratedPlan(BaseModel):
    Plan: List[str]


class Dependencies(BaseModel):
    Dependencies: List[str]


class CodeGeneration(BaseModel):
    Thought: str
    Generated_Code: str


class InitialCode(BaseModel):
    Timestamp: datetime
    Documentation_Scraping: DocumentationScraping
    Generated_Plan: GeneratedPlan
    Dependencies: Dependencies
    Coding_Agent: CodeGeneration


class LintingAttempt(BaseModel):
    Timestamp: datetime
    lint_attempt: int
    Code: Optional[str] = None
    Lint_Query_Result: Optional[str] = None
    Lint_Response: Optional[str] = None
    Generated_Code: Optional[CodeGeneration] = None
    Lint_Result: List[str]
    Metric: int


class CorrectionLoop(BaseModel):
    Timestamp: datetime
    Error1: str
    Generated_Code: CodeGeneration
    Lint_Result: List[str]
    Metric: int
    Error2: str


class SelfHealingBlock(BaseModel):
    time: float
    Generation_ID: int
    Linting_Loop: List[LintingAttempt]
    Correction_Loop: CorrectionLoop
    Metric: int


class Task(BaseModel):
    Task_ID: int
    Task: str
    Metric: int
    Time: datetime
    TaskExecutorConfig: TaskExecutionConfig
    Initial_Code: InitialCode
    Generation_Attempts: List[SelfHealingBlock]


class Run(BaseModel):
    Timestamp: datetime
    Run_ID: int
    Git_SHA: Tuple[str]
    Commit_Message: Tuple[str]
    Tasks: List[Task]


if __name__ == "__main__":
    from codinit.experiment_tracking.json_experiment_rw import (
        read_from_json,
        write_to_json,
    )

    # TaskExecutionConfig instance
    task_executor_config = TaskExecutionConfig(
        execute_code=True,
        install_dependencies=True,
        check_package_is_in_pypi=True,
        log_to_stdout=True,
        coding_attempts=1,
        max_coding_attempts=5,
        dependency_install_attempts=5,
        planner_temperature=0.0,
        coder_temperature=0.0,
        code_corrector_temperature=0.0,
        dependency_tracker_temperature=0.0,
        lint_correction_threshold=3,
    )

    # InitialCode instance
    initial_code = InitialCode(
        Timestamp=datetime.now(),
        Documentation_Scraping=DocumentationScraping(
            Relevant_Docs="Doc1", num_tokens=500
        ),
        Generated_Plan=GeneratedPlan(Plan=["Step 1", "Step 2"]),
        Dependencies=Dependencies(Dependencies=["lib1", "lib2"]),
        Coding_Agent=CodeGeneration(
            Thought="Thinking about the solution",
            Generated_Code="print('Hello, World!')",
        ),
    )

    # LintingAttempt instance
    linting_attempt = LintingAttempt(
        Timestamp=datetime.now(),
        lint_attempt=1,
        Code="print('Hello, World!')",
        Lint_Query_Result="Query result",
        Lint_Response="Response",
        Generated_Code=CodeGeneration(
            Thought="Correcting based on linting",
            Generated_Code="print('Hello, World!')",
        ),
        Lint_Result=["Error 1", "Error 2"],
        Metric=2,
    )

    # CorrectionLoop instance
    correction_loop = CorrectionLoop(
        Timestamp=datetime.now(),
        Error1="Error1 details",
        Generated_Code=CodeGeneration(
            Thought="Fixing Error1", Generated_Code="print('Fixed Hello, World!')"
        ),
        Lint_Result=["Error 3"],
        Metric=1,
        Error2="Error2 details",
    )

    # SelfHealingBlock instance
    self_healing_block = SelfHealingBlock(
        time=2.5,
        Generation_ID=101,
        Linting_Loop=[linting_attempt],
        Correction_Loop=correction_loop,
        Metric=3,
    )

    # Task instance
    task = Task(
        Task_ID=1,
        Task="Implement feature X",
        Metric=85,
        Time=datetime.now(),
        TaskExecutorConfig=task_executor_config,
        Initial_Code=initial_code,
        Generation_Attempts=[self_healing_block],
    )

    # Run instance
    run = Run(
        Timestamp=datetime.now(),
        Run_ID=123456789,
        Git_SHA=("abcdef12345",),
        Commit_Message=("Implemented feature X",),
        Tasks=[task],
    )

    # Serialize to JSON
    print(run.model_dump_json(indent=4))
    write_to_json(file_path="data/dummy_run.json", data=run)

    # Deserialize from JSON
    run_from_json = read_from_json(file_path="data/dummy_run.json")
