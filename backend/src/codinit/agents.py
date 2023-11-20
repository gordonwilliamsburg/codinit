import inspect
import json
import re
import time
from inspect import Parameter
from typing import Any, Callable, List, Optional, Union

import openai
from openai import ChatCompletion
from openai.error import RateLimitError
from pydantic import create_model
from tenacity import retry, stop_after_attempt, wait_random_exponential

from codinit.config import agent_settings, secrets
from codinit.prompts import (
    code_corrector_system_prompt,
    code_corrector_user_prompt_template,
    coder_system_prompt,
    coder_user_prompt_template,
    dependency_tracker_system_prompt,
    dependency_tracker_user_prompt_template,
    planner_system_prompt,
    planner_user_prompt_template,
)
from codinit.pydantic_models import OpenAIResponse

openai.api_key = secrets.openai_api_key


class OpenAIAgent:
    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        system_prompt: str = "",
        user_prompt_template="",
        functions: List[Callable[..., Any]] = [],
    ):
        self.model = model
        self.functions = functions
        self.func_names = [func.__name__ for func in self.functions]
        self.system_prompt = system_prompt
        self.user_prompt_template = user_prompt_template

    def get_schema(self, function: Callable[..., Any]):
        # function to extract schema of a function from the function code
        kw = {
            n: (o.annotation, ... if o.default == Parameter.empty else o.default)
            for n, o in inspect.signature(function).parameters.items()
        }
        parameters = create_model(f"Input for `{function.__name__}`", **kw).schema()
        function_schema = dict(
            name=function.__name__, description=function.__doc__, parameters=parameters
        )
        return function_schema

    def call_func(self, response: OpenAIResponse) -> Any:
        """
        Extract name and arguments of the function from the response from the OpenAI ChatCompletion API,
        Get the corresponding function from the current file,
        then call the function with extracted arguments.
        """
        fc = response.choices[0].message.function_call
        if fc and fc.name not in self.func_names:
            return print(f"Not allowed: {fc.name}")
        if fc:
            f = globals()[fc.name]
            print(fc.arguments)
            return f(**json.loads(fc.arguments))

    @retry(
        wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3)
    )
    def call_gpt(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        functions=None,
        function_name: str = "",
    ) -> Union[OpenAIResponse, Exception]:
        """
        Calls the GPT model and returns the completion.

        Args:
        - user_prompt (str): The prompt provided by the user.
        - system_prompt (Optional[str]): An optional system prompt.
        - model (str): The GPT model version. Default is "gpt-3.5-turbo".
        - functions: list of function schemas
        - function_name: name of the function to be called to force model to use function.

        Returns:
        - Any: The result from ChatCompletion.
        """

        # Start by adding the user's message to the messages list
        messages = [{"role": "user", "content": user_prompt}]

        # If there's a system prompt, insert it at the beginning of the messages list
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})
        try:
            # Call the ChatCompletion API to get the model's response and return the result
            response = ChatCompletion.create(
                model=self.model,
                messages=messages,
                functions=functions,
                function_call={"name": function_name},
            )

            # Convert the response to an OpenAIResponse object and return
            return OpenAIResponse(**response)
        except RateLimitError as e:
            print("Rate limit reached, waiting to retry...")
            print(f"Exception: {e}")
            # TODO adjust this constant time to extract the wait time is reported in the exception
            wait_time = 10
            time.sleep(wait_time)
            raise
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            raise  # Re-raise the exception to trigger the retry mechanism

    def execute(self, function_name: str, **kwargs):
        user_prompt = self.user_prompt_template.format(**kwargs)
        function_schemas = [self.get_schema(function=func) for func in self.functions]
        gpt_response = self.call_gpt(
            user_prompt=user_prompt,
            system_prompt=self.system_prompt,
            functions=function_schemas,
            function_name=function_name,
        )
        # print(gpt_response)
        function_output = self.call_func(gpt_response)
        # print(function_output)
        return function_output


def extract_code_from_text(text):
    pattern = re.compile(r"```python(.*?)```", re.DOTALL)
    match = pattern.search(text)
    if match:
        code = match.group(1).strip()
        return code
    else:
        return text.strip()  # Return original text without Markdown quotes


def remove_magic_commands(code: str) -> str:
    # Regular expression to match lines that start with `!pip install`
    pattern = re.compile(r"^\s*!pip install.*$", re.MULTILINE)

    # Use re.sub() to replace those lines with an empty string
    cleaned_code = re.sub(pattern, "", code)
    # TODO: sometimes, the only thing returned by the code is a magic command
    # for example !pip install openai
    # when this is removed, the linter throws an error because it finds no code to parse
    # need to check at the linter side if code is empty.
    return cleaned_code


def execute_plan(steps: List[str]) -> List[str]:
    """
    takes the plan as a list of steps (str) and executes it
    """
    return steps


def install_dependencies(deps: List[str]) -> List[str]:
    """
    takes the list of python dependencies as list of strings deps: List[str]
    and installs them
    """
    return deps


def execute_code(thought: str, code: str):
    """
    Executes python code. Input:
    thought: An explanation of what your code is doing
    code: a JSON compatible one-line string that contains python code. A one-line string!
    """
    code = extract_code_from_text(code)
    code = remove_magic_commands(code)
    print(code)
    return code


planner_agent = OpenAIAgent(
    model=agent_settings.planner_model,
    system_prompt=planner_system_prompt,
    user_prompt_template=planner_user_prompt_template,
    functions=[execute_plan],
)
dependency_agent = OpenAIAgent(
    model=agent_settings.dependency_model,
    system_prompt=dependency_tracker_system_prompt,
    user_prompt_template=dependency_tracker_user_prompt_template,
    functions=[install_dependencies],
)
coding_agent = OpenAIAgent(
    model=agent_settings.coder_model,
    system_prompt=coder_system_prompt,
    user_prompt_template=coder_user_prompt_template,
    functions=[execute_code],
)
code_correcting_agent = OpenAIAgent(
    model=agent_settings.code_corrector_model,
    system_prompt=code_corrector_system_prompt,
    user_prompt_template=code_corrector_user_prompt_template,
    functions=[execute_code],
)

if __name__ == "__main__":
    context = """
    Read CSV Files
    A simple way to store big data sets is to use CSV files (comma separated files).

    CSV files contains plain text and is a well know format that can be read by everyone including Pandas.

    In our examples we will be using a CSV file called 'data.csv'.

    Download data.csv. or Open data.csv

    ExampleGet your own Python Server
    Load the CSV into a DataFrame:

    import pandas as pd

    df = pd.read_csv('data.csv')

    print(df.to_string())
    """
    task = "write code that reads a csv file using the pandas library"
    plan = planner_agent.execute(
        function_name="execute_plan",
        context=context,
        task=task,
    )
    # TODO: check that plan is not none
    dependencies = dependency_agent.execute(
        function_name="install_dependencies", plan=plan
    )
    code = coding_agent.execute(
        function_name="execute_code",
        task=task,
        context=context,
        plan=plan,
        source_code="",
    )
    code = code_correcting_agent.execute(
        function_name="execute_code",
        task=task,
        context=context,
        source_code=code,
        error="",
    )
