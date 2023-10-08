"""
Code from https://github.com/ChuloAI/code-it/tree/40b9ed946019bb24fa0e172edb679df73abb62ba/code_it/code_editor
Just added comments
"""
import logging
import os
import random
import string
import subprocess
from typing import List

from virtualenv import cli_run

logger = logging.getLogger(__name__)

RANDOM_NAME_LENGTH = 16


class VirtualenvManager:
    """A class to manage a Python virtual environment."""

    def __init__(self, name: str = "", base_path: str = "/tmp") -> None:
        """
        Initialize the VirtualenvManager instance.

        Args:
            name (str): The name of the virtual environment. Defaults to "".
            base_path (str): The path where the virtual environment is to be created. Defaults to "/tmp".
        """
        # Check if a name was provided
        if not name:
            # Generate a random string of length RANDOM_NAME_LENGTH
            name = "".join(
                random.choice(string.ascii_letters + string.digits)
                for _ in range(RANDOM_NAME_LENGTH)
            )
        self.name = name  # set the name of the virtual environment
        self.path = os.path.join(
            base_path, name
        )  # form the full path of the virtual environment
        self.python_interpreter = os.path.join(
            self.path, "bin/python3"
        )  # set the path of the Python interpreter
        self.dependencies: List[str] = []  # initialize an empty list for dependencies

    def add_dependency(self, dependency: str) -> None:
        """
        Add a dependency to the virtual environment.

        Args:
            dependency (str): The name of the dependency.
        """
        # Logging the addition of dependency
        logger.info("Adding dependency '%s' ", dependency)
        # Append the dependency to the list
        self.dependencies.append(dependency)

    def create_env(self) -> None:
        """
        Create the virtual environment at the specified path.
        """
        # Logging the creation of virtual environment
        logger.info("Creating virtualenv at path '%s' ", self.path)
        # Creating the virtual environment using virtualenv's cli_run function
        cli_run([self.path], setup_logging=False)

    def install_dependencies(self) -> subprocess.CompletedProcess:
        """
        Install the dependencies in the virtual environment.

        Returns:
            CompletedProcess: A subprocess.CompletedProcess instance which contains information
                              about the completed process related to the installation of dependencies.
        """
        # Logging the installation of dependencies
        logger.info("Installing dependencies")
        # Installing the dependencies using subprocess module
        process = subprocess.run(
            [self.python_interpreter, "-m", "pip", "install"]
            + self.dependencies,  # cmd: python3 -m pip install <dependencies>
            capture_output=True,
            text=True,
        )
        # Return the completed process
        return process


class CodeEditorTooling:
    """
    A Python source code editor class that abstracts interactions with source code files in Python.
    It supports editing, saving, and running Python scripts dynamically.
    The class maintains the code in memory and persistently in a file, which can be executed using a Python interpreter.
    """

    def __init__(self, filename="magic_code.py", interpreter="python3") -> None:
        """
        Initialize the class with a filename and interpreter. By default, these are "magic_code.py" and "python3" respectively.
        """
        self.source_code: List[
            str
        ] = []  # Initialize an empty list to hold source code lines.
        self.filename = (
            filename  # Store the filename where the code will be saved and run from.
        )
        self.interpreter = (
            interpreter  # Store the name of the interpreter to run the code with.
        )

    def overwrite_code(self, new_source: str) -> str:
        """
        Overwrite the source code with a new string, split it into lines, save it, and display it.
        """
        # Split the input string into lines and store them in the source code list.
        new_lines_of_code = [line for line in new_source.split("\n") if line]
        self.source_code = (
            new_lines_of_code  # Overwrite the existing source code with the new lines.
        )
        self.save_code()  # Save the new code to the file.
        return self.display_code()  # Display the new code.

    def add_code(self, add_code_input: str) -> str:
        """
        Add more lines to the existing source code, save it, and display it.
        """
        # Split the input string into lines and append them to the source code list.
        new_lines_of_code = [line for line in add_code_input.split("\n") if line]
        self.source_code.extend(
            new_lines_of_code
        )  # Add the new lines to the existing source code.
        self.save_code()  # Save the updated code to the file.
        return self.display_code()  # Display the updated code.

    def change_code_line(
        self, change_code_line_input: str
    ) -> str:  # TODO provide more specification of input
        """
        Change a specific line in the source code, save it, and display it.
        input should be of the form:
        # "line number \n code"
        """
        # Split the input string into the line number and the new code for that line.
        s = change_code_line_input.split("\n")
        line = int(s[0]) - 1  # The line number (0-indexed).
        code = s[1]  # The new code for the line.
        self.source_code[line] = code  # Replace the old line of code with the new one.
        self.save_code()  # Save the updated code to the file.
        return self.display_code()  # Display the updated code.

    def delete_code_lines(
        self, delete_code_lines_input: str
    ) -> str:  # TODO provide more specification of input
        """
        Delete specific lines in the source code, save it, and display it.
        input should be of the form ?
        """
        # Split the input string into line numbers, sort them in reverse order, and delete each line from the source code.
        lines_to_delete = [int(x) for x in delete_code_lines_input.split(",")]
        lines_to_delete.sort()
        lines_to_delete.reverse()
        for line in lines_to_delete:
            idx = line - 1  # The line number (0-indexed).
            self.source_code.pop(idx)  # Remove the line from the source code.
        self.save_code()  # Save the updated code to the file.
        return self.display_code()  # Display the updated code.

    def save_code(self):
        """
        Save the source code to a file.
        """
        with open(self.filename, "w") as fp:  # Open the file in write mode.
            fp.write("\n".join(self.source_code))  # Write the source code to the file.

    def run_code(self):
        """
        Run the source code using the specified Python interpreter, and return the results.
        """
        # Use the subprocess module to run the code in a separate process.
        completed_process = subprocess.run(
            [self.interpreter, self.filename], capture_output=True, timeout=30
        )

        # Print the completed process and any stderr.
        print(completed_process, completed_process.stderr)

        # Determine if the program succeeded based on its return code.
        succeeded = "Succeeded" if completed_process.returncode == 0 else "Failed"

        # Extract the stdout and stderr from the completed process.
        stdout = completed_process.stdout
        stderr = completed_process.stderr

        # Return a string containing the results.
        return f"Program {succeeded}\nStdout:{stdout}\nStderr:{stderr}"

    def run_script_inside_env(
        self, script_path: str, *args
    ) -> subprocess.CompletedProcess:
        """
        Run a Python script inside the virtual environment.

        Args:
            script_path (str): The path to the Python script to run.
            *args: Additional arguments to pass to the script.

        Returns:
            CompletedProcess: A subprocess.CompletedProcess instance containing information about the completed process.
        """
        # Logging the script execution
        logger.info(f"Running script '{script_path}' inside virtual environment'")

        # Execute the script using the virtual environment's Python interpreter
        process = subprocess.run(
            [self.interpreter, script_path] + list(args), capture_output=True, text=True
        )

        return process

    def display_code(self) -> str:
        """
        Return a string representation of the current source code.
        """
        code_string = "\n"  # Initialize an empty string to hold the code.
        for line in self.source_code:  # For each line in the source code...
            code_string += f"{line}\n"  # ...add it to the string.
        return code_string  # Return the string representation of the code.
