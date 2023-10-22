# Experiment Tracking
We log experiments under the following hierarchy:
- Run_ID: str, id of the run which comprises of a set of tasks.
- Git_SHA: str, the git sha corresponding to the run
- Commit_Message: str, the commit message corresponding to the git sha
    - Task_ID: int, id of a task, which corresponds to a set of generation attempts
    - Task: str, description of the task
        - Generation_ID: int, id of the generation attempt
        - Code: str, corresponds the the code generated in the coding attempt
        - Linter_Output: List[str], corresponds to the list of errors detected by the linter
        - Metric: int, corresponds to the metric computed from the linter output, here the sum of errors
        - Error_Log: str, the error log obrtained from python subprocess after executing the code
        - Timestamp: datetime, corresponds to the time of the code generation

# Metrics
# TODO
Add metric for when agent generates same errors
