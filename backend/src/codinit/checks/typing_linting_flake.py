import subprocess


def run_flake8(filename):
    try:
        # If there are no issues, the command will complete without an error
        result = subprocess.run(
            ["flake8", filename], check=True, text=True, capture_output=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        # If there are issues, they will be captured here
        return e.stdout


def run_isort(filename):
    try:
        result = subprocess.run(
            ["isort", filename], check=True, text=True, capture_output=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stdout


def run_mypy(filename):
    try:
        result = subprocess.run(
            ["mypy", filename], check=True, text=True, capture_output=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stdout


def run_pylint(filename):
    try:
        result = subprocess.run(
            ["pylint", filename], check=True, text=True, capture_output=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stdout


filename = "src/codinit/checks/sample_code.py"
# flake8_output = run_flake8(filename)
# print(flake8_output)
# mypy_output = run_mypy(filename)
# print(mypy_output)
# pylint_output = run_pylint(filename)
# print(pylint_output)
isort_output = run_isort(filename)
print(isort_output)
