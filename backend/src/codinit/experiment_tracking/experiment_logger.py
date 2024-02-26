import json
from datetime import datetime
from typing import List, Tuple

from codinit.experiment_tracking.experiment_pydantic_models import (
    CorrectionLoop,
    InitialCode,
    LintingAttempt,
    Run,
    SelfHealingBlock,
    Task,
    TaskExecutionConfig,
)
from codinit.experiment_tracking.json_experiment_rw import read_from_json, write_to_json


class ExperimentLogger:
    def __init__(
        self,
    ):
        # self.documentation_scraping = None
        # self.code_generation = []
        self.init_lint_attempt_logs()
        self.init_correction_loop_logs()
        self.self_healing_blocks: List[SelfHealingBlock] = []
        # self.linting_attempts = []
        # self.correction_loops = []

    def log_initial_code(self, initial_code: InitialCode):
        self.initial_code = initial_code

    # def log_code_generation(self, data):
    #     self.code_generation.append(data)

    def init_lint_attempt_logs(self):
        self.linting_attempts = []

    def log_linting_attempt(self, linting_attempt: LintingAttempt):
        self.linting_attempts.append(linting_attempt)

    def init_correction_loop_logs(self):
        self.correction_loops = []

    def log_correction_loop(self, correction_loop: CorrectionLoop):
        self.correction_loop = correction_loop

    def log_self_healing_block(self, time: float, generation_id: int):
        self_healing_block = SelfHealingBlock(
            time=time,
            Generation_ID=generation_id,
            Metric=sum(
                [linting_attempt.Metric for linting_attempt in self.linting_attempts]
            )
            + self.correction_loop.Metric,
            Linting_Loop=self.linting_attempts,
            Correction_Loop=self.correction_loop,
        )
        self.self_healing_blocks.append(self_healing_block)

    def compile_task(
        self,
        task_id: int,
        task_description: str,
        time_stamp: datetime,
        task_execution_config: TaskExecutionConfig,
    ):
        self.task = Task(
            Task_ID=task_id,
            Task=task_description,
            Time=time_stamp,
            TaskExecutorConfig=task_execution_config,
            Initial_Code=self.initial_code,
            Generation_Attempts=self.self_healing_blocks,
            Metric=sum(
                [
                    self_healing_block.Metric
                    for self_healing_block in self.self_healing_blocks
                ]
            ),
        )

    def log_task_to_run(
        self,
        time_stamp: datetime,
        run_id: int,
        git_sha: Tuple[str],
        commit_message: Tuple[str],
    ):
        self.run = Run(
            Timestamp=time_stamp,
            Run_ID=run_id,
            Git_SHA=git_sha,
            Tasks=[self.task],
            Commit_Message=commit_message,
        )

    def save_to_json(self):
        save_dir = f"data/experiment_logs/Run_{self.run.Run_ID}"
        file_name = (
            f"task_{self.task.Task_ID}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        )
        write_to_json(self.run, f"{save_dir}/{file_name}")
