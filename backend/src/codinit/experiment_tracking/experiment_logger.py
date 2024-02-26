import json
from datetime import datetime

from codinit.experiment_tracking.experiment_pydantic_models import (
    DocumentationScraping,
    InitialCode,
    LintingAttempt,
    SelfHealingBlock,
    Task,
)


class ExperimentLogger:
    def __init__(self, task_id: int):
        self.task_id = task_id
        # self.documentation_scraping = None
        # self.code_generation = []
        self.init_lint_attempt_logs()
        # self.correction_loops = []

    def log_initial_code(self, initial_code: InitialCode):
        self.initial_code = initial_code

    # def log_code_generation(self, data):
    #     self.code_generation.append(data)

    def init_lint_attempt_logs(self):
        self.linting_attempts = []

    def log_linting_attempt(self, linting_attempt: LintingAttempt):
        self.linting_attempts.append(linting_attempt)

    # def log_correction_loop(self, data):
    #     self.correction_loops.append(data)

    # def compile_task(self):
    #     # Assuming the first element of each list is the initial one
    #     initial_code = InitialCode(
    #         Documentation_Scraping=self.documentation_scraping[0],
    #         Generated_Plan=self.code_generation[0],
    #         Dependencies=self.dependencies[0],  # Assuming you have a method to log dependencies
    #         Coding_Agent=self.code_generation[0]
    #     )

    #     self_healing_blocks = [SelfHealingBlock(
    #         Linting_Loop=linting_attempt,
    #         Correction_Loop=correction_loop,
    #         # Other fields...
    #     ) for linting_attempt, correction_loop in zip(self.linting_attempts, self.correction_loops)]

    #     return Task(
    #         Task_ID=self.task_id,
    #         Task="Your task description here",  # You may want to log this somewhere
    #         Metric=calculate_metric(self_healing_blocks),  # Implement this function based on your metric calculation
    #         Time=datetime.now(),  # Or log the start time of the task
    #         TaskExecutorConfig=TaskExecutionConfig(),  # Initialize appropriately
    #         Initial_Code=self.initial_code,
    #         Generation_Attempts=self_healing_blocks
    #     )

    # def save_to_json(self):
    #     task = self.compile_task()
    #     file_name = f"task_{self.task_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    #     with open(file_name, 'w') as file:
    #         json.dump(task.dict(), file, indent=4)
