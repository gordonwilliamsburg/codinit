from typing import List, Optional

from pydantic import BaseModel

"""
# Represents the usage statistics for the completion request.
class Usage(BaseModel):
    prompt_tokens: int  # Number of tokens in the prompt.
    completion_tokens: int  # Number of tokens in the generated completion.
    total_tokens: int  # Total number of tokens used in the request (prompt + completion).


# Represents the function call details generated by the model.
class FunctionCall(BaseModel):
    name: str  # The name of the function to call.
    arguments: str  # The arguments to call the function with, in JSON format. Validate before use.


# Represents the chat completion message generated by the model.
class Message(BaseModel):
    role: str  # The role of the author of this message.
    content: Optional[str]  # The contents of the message.
    function_call: Optional[
        FunctionCall
    ]  # The name and arguments of a function to be called.


# Represents each choice in the chat completion response.
class Choice(BaseModel):
    index: int  # The index of the choice in the list of choices.
    message: Message  # A chat completion message generated by the model.
    finish_reason: str  # The reason the model stopped generating tokens (e.g., "stop", "function_call").



ChatCompletion Response has the following hierarchy:
OpenAIResponse
├── id: string
├── object: string
├── created: integer
├── model: string
├── choices: array
│   └── Choice
│       ├── index: integer
│       ├── message: Message
│       │   ├── role: string
│       │   ├── content: string (or null)
│       │   └── function_call (optional)
│       │       └── FunctionCall
│       │           ├── name: string
│       │           └── arguments: string
│       └── finish_reason: string
└── usage: Usage
    ├── prompt_tokens: integer
    ├── completion_tokens: integer
    └── total_tokens: integer


# Represents the chat completion response returned by the model.
class OpenAIResponse(BaseModel):
    id: str  # A unique identifier for the chat completion.
    object: str  # The object type, always "chat.completion".
    created: int  # The Unix timestamp (in seconds) of when the chat completion was created.
    model: str  # The model used for the chat completion.
    choices: List[Choice]  # A list of chat completion choices.
    usage: Usage  # Usage statistics for the completion request.
"""
