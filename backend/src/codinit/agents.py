import abc
import re

from langchain import LLMChain, PromptTemplate
from langchain.memory import ConversationBufferMemory

from codinit.prompts import (
    code_corrector_prompt,
    coder_prompt,
    dependency_tracker_prompt,
    planner_prompt,
)


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

    return cleaned_code


class BaseAgent:
    def __init__(self, llm) -> None:
        self.llm = llm

    @abc.abstractmethod
    def parse_output(self, raw_result):
        raise NotImplementedError()

    def execute_task(self, **kwargs):
        prompt = PromptTemplate(
            input_variables=list(kwargs.keys()) + ["chat_history"],
            template=self.prompt_template,
        )
        memory = ConversationBufferMemory(
            memory_key="chat_history", input_key=self.input_key
        )
        llm_chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            verbose=False,
            memory=memory,
        )
        raw_result = llm_chain.predict(**kwargs)
        # print("--------------------------raw result-------------------")
        # print(raw_result)
        # if self.stop_string in raw_result:
        #    raw_result = raw_result.split(self.stop_string)[0]
        parsed_result = self.parse_output(raw_result)
        # print("--------------------------parsed result-------------------")
        # print(parsed_result)
        return parsed_result


class Coder(BaseAgent):
    def __init__(self, llm) -> None:
        super().__init__(llm)
        self.stop_string = "End Of Code."
        self.input_key = "objective"
        self.prompt_template = coder_prompt

    def parse_output(self, result):
        result = result.replace("End Of Code.", "")
        result = remove_magic_commands(result)
        return result


class CodeCorrector(BaseAgent):
    def __init__(self, llm) -> None:
        super().__init__(llm)
        self.stop_string = "End Of Code"
        self.input_key = "source_code"
        self.prompt_template = code_corrector_prompt

    def parse_output(self, result):
        # Extract the thought
        match_thought = re.search(r"Thought:(.*?)New Code:", result, re.DOTALL)
        thought = (
            match_thought.group(1).strip() if match_thought else "Thought not found."
        )

        print(thought)
        # Extract the code
        match_code = re.search(r"New Code:(.*?)End Of Code", result, re.DOTALL)
        code = match_code.group(1).strip() if match_code else "Code not found."
        code = extract_code_from_text(code)
        code = remove_magic_commands(code)
        # Print the thought and code
        # print("Thought:\n", thought)
        # print("\nCode:\n", code)
        return code


class Planner(BaseAgent):
    def __init__(self, llm) -> None:
        super().__init__(llm)
        self.stop_string = "End of planning flow."
        self.input_key = "task"
        self.prompt_template = planner_prompt

    def parse_output(self, steps):
        if "Steps:" in steps:
            steps = steps.split("Steps:")[1]
        if "End of planning flow" in steps:
            steps = steps.split("End of planning flow")[0]
        # print(f"planner steps {steps}")
        # print("----------")

        # Split the string based on step numbers
        split_steps = re.split(r"(\d+\.)", steps)

        # Combine step numbers with step content and remove any empty strings
        steps = [
            split_steps[i] + split_steps[i + 1].strip()
            for i in range(1, len(split_steps), 2)
        ]

        return steps


class DependencyTracker(BaseAgent):
    def __init__(self, llm) -> None:
        super().__init__(llm)
        self.stop_string = "end of planning flow"
        self.input_key = "plan"
        self.prompt_template = dependency_tracker_prompt

    def parse_output(self, output):
        output = output.lower()
        # print(f"dependency tracker output {output}")
        # print("----------")
        if self.stop_string in output:
            output = output.split(self.stop_string)[0]
            # print (f'dependency tracker output {output}')
            # print('----------')
        return [step.split(".")[0] for step in output.split("\n") if len(step) > 0]
