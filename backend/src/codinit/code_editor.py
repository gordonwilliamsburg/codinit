"""
code from https://github.com/ChuloAI/code-it/blob/40b9ed946019bb24fa0e172edb679df73abb62ba/code_it/code_editor/python_editor.py
Just added comments
"""
import json
import logging
import subprocess
from typing import Dict, List

import isort

from codinit.base_models import CodeEditorTooling, VirtualenvManager
from codinit.checks.get_imports import extract_library_usages
from codinit.checks.move_imports import refactor_code

# Set up the logger
logger = logging.getLogger(__name__)


class PythonCodeEditor(CodeEditorTooling):
    """A class for managing Python code editing in a virtual Python environment."""

    def __init__(self, filename="magic_code.py") -> None:
        """
        Initialize the PythonCodeEditor instance.

        Args:
            filename (str): The name of the file to store the code. Defaults to "magic_code.py".
        """
        # Call the parent class initializer with the provided filename and "python3" as the interpreter
        super().__init__(filename, interpreter="python3")

        # Instantiate a VirtualenvManager
        self.venv = VirtualenvManager()

    def add_dependency(self, dependency: str):
        """
        Add a dependency to the virtual environment.

        Args:
            dependency (str): The name of the dependency.
        """
        # Add the dependency to the virtual environment
        self.venv.add_dependency(dependency)

    def create_env(self):
        """
        Create the virtual environment and set the Python interpreter.
        """
        # Create the virtual environment
        self.venv.create_env()

        # Set the Python interpreter to the one from the virtual environment
        self.interpreter = self.venv.python_interpreter

        # Log the set interpreter
        logger.info("Python interpreter set to %s", self.interpreter)

    def install_dependencies(self):
        """
        Install the dependencies in the virtual environment.

        Returns:
            CompletedProcess: A subprocess.CompletedProcess instance which contains information
                              about the completed process related to the installation of dependencies.
        """
        # Install the dependencies and get the subprocess.CompletedProcess instance
        process = self.venv.install_dependencies()

        # Return the process
        return process

    def process_imports(self, code: str, library_name: str) -> str:
        """
        refactor code to move all library imports to top of the file and runs isort for import sorting
        """
        if len(code) > 0:
            refactored_code = refactor_code(code=code, library_name=library_name)
            sorted_code = isort.code(refactored_code)
            return sorted_code
        else:
            return code

    def validate_code_imports(self, code: str, dependencies: List[str]):
        final_result: Dict[str, bool] = {}
        for library_name in dependencies:
            # extract imports, returns a list of import_paths
            # e.g. for the following code:
            # it returns: ['langchain.llms', 'langchain.prompts', 'langchain.LLMChain', 'langchain.agents']
            imports = extract_library_usages(code=code, library_name=library_name)
            print(imports)
            # imports = ["langchain.llms", "langchain.prompts", "langchain.LLMChain", "langchain.agents"]
            json_imports = json.dumps(imports)  # Convert list to JSON string
            # Writing to sample.json
            with open("sample.json", "w") as file:
                json.dump(imports, file)
            result = self.run_script_inside_env(
                "src/codinit/checks/check_import_existence.py",
                json_imports,
                library_name,
            )
            print(result.stdout)
            if result.stderr:
                print("Error from script:", result.stderr)
            elif result.stdout:
                parsed_result = json.loads(result.stdout)  # Extract stdout and parse it
                final_result |= parsed_result
                # Print the output of the script
        return final_result

    def validate_code_references(self, dependencies: List[str]):
        final_result: Dict[str, bool] = {}
        for library_name in dependencies:
            result = self.run_script_inside_env(
                "src/codinit/checks/check_reference_existence.py",
                self.filename,
                library_name,
            )
            if result.stderr:
                print("Error from script:", result.stderr)
            elif result.stdout:
                parsed_result = json.loads(result.stdout)  # Extract stdout and parse it
                # Print the output of the script
                final_result |= parsed_result
        return final_result

    def run_linter(self):
        cmd = [
            "pylint",
            self.filename,
            "--disable=all",
            "--enable=E0401,E0611,E0402,E0602,E0603,E0604,W1505,E1102,E1101",
        ]

        # Run pylint
        linter_output = subprocess.run(cmd, text=True, capture_output=True, check=False)
        linter_output = linter_output.stdout.splitlines()
        error_messages = [
            line for line in linter_output if line.startswith(self.filename)
        ]
        # Extract the number of issues from the output
        return error_messages
