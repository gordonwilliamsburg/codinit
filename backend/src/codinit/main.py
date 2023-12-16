import csv
import subprocess
from typing import Tuple

from codinit.code_editor import PythonCodeEditor
from codinit.config import eval_settings
from codinit.task_executor import TaskExecutionConfig, TaskExecutor

TASKS = [
    "using langchain library, write code that answers a question over a given text.",
    "using the langchain library, write code for an agent that answers math questions.",
    "using the langchain library, write code that automatically gives information about the weather.",
    "using the langchain library, write code for a coding agent that writes python code based on prompts.",
    "using the langchain library, write code to answer some questions by reading wikipedia articles.",
]

"""
    "using the langchain library, write code for an agent that collects information about products from the internet and gives a competitor analysis.",
    "using the langchain library, write code that summarizes a pdf document.",
    "using the langchain library, write code that for an agent that writes stories.",
    "using the langchain library, write code for an agent that translates text.",
    "using the langchain library, write code for an agent that writes a Jira ticket based on a conversation with the user.",
    "using the langchain library, write code for a research agent that collects papers related to a specific topic and generates a summary of the research.",
"""


def get_git_info() -> Tuple[str, str]:
    sha = subprocess.getoutput("git rev-parse HEAD")
    message = subprocess.getoutput("git log -1 --pretty=%B")
    return sha, message


def main():
    # Get git info
    sha, message = get_git_info()

    # Open or create CSV file for appending
    with open(eval_settings.eval_dataset_location, "a+", newline="") as csvfile:
        fieldnames = [fieldname for fieldname in eval_settings.eval_columns]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Check if the CSV is empty, if so, write the header
        csvfile.seek(0)
        if not csvfile.read():
            writer.writeheader()

        # Get the last Run_ID and increment it
        csvfile.seek(0)
        last_run_id = 0
        for row in csv.reader(csvfile):
            try:
                last_run_id = int(row[0])
            except ValueError:
                pass

        run_id = last_run_id + 1
        for task_id, task in enumerate(TASKS):
            code_editor = PythonCodeEditor()
            config = TaskExecutionConfig()
            task_executor = TaskExecutor(
                code_editor=code_editor,
                config=config,
                task=task,
                run_id=run_id,
                task_id=task_id,
                sha=sha,
                message=message,
                csv_writer=writer,
            )
            print("---------new_task-----------")
            task_executor.execute_and_log(
                source_code="",
                libraries=[],
            )


if __name__ == "__main__":
    main()
