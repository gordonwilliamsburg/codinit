# Extracting Schema from a Python function
The function `schema` takes a python function and returns the schema compatible with the expected `ChatCompletion` API call. It returns a dictionary of the form:
```json
{"name": func_name,
"description": func_docstring,
"parameters": dict of function parameters
}
```
The more extended version has the following hierarchy:
- **name**: String
  - Description: The function's name.

- **description**: String
  - Description: The function's docstring.

- **parameters**: Dictionary
  - **title**: String
    - Description: A descriptive title for the input parameters.
  - **type**: String
    - Description: Indicates it's an 'object'.
  - **properties**: Dictionary
    - Description: Each key represents a parameter name and its value provides details about the parameter.
    - **Parameter Name**: Dictionary
      - **title**: String
        - Description: A title for the parameter.
      - **type**: String
        - Description: The datatype of the parameter.
      - **default** (Optional): Variant Types (like Integer, String, etc.)
        - Description: The default value of the parameter if it has one.
  - **required**: List[String]
    - Description: List of parameter names that are required.

For example, the following addition function:
```python
def sums(a: int, b: int = 1):
    """
    Adds a + b
    """
    return a + b
```
will produce the following schema:
```json
{'name': 'sums',
 'description': '\n    Adds a + b\n    ',
 'parameters': {'title': 'Input for `sums`',
  'type': 'object',
  'properties': {'a': {'title': 'A', 'type': 'integer'},
   'b': {'title': 'B', 'default': 1, 'type': 'integer'}},
  'required': ['a']}}
```
The function signature is as follows:
```python
def schema(f: Callable[..., Any])
```

where `Callable[..., Any]` This represents a callable (or function) that can take any number of arguments (...) and returns any type (Any). This is a broad hint that allows for any function, regardless of its signature.

# OpenAI ChatCompletion Response Model
```bash
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

```
