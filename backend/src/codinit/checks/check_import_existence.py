import importlib
import json
import sys
from typing import Dict, List


def check_import_exists(library_name: str, import_name: str) -> bool:
    """
    Check if a specific import exists in a library.

    Parameters:
    - library_name: Name of the library/module to inspect.
    - import_name: The full path of the import to check.

    Returns:
    - True if the import exists, False otherwise.
    """
    try:
        # Split import name by '.' to handle nested modules or attributes.
        parts = import_name.split(".")

        # Start with the main library/module
        module = importlib.import_module(parts[0])
        if parts[0] != library_name:  # Ensure the base module is the target library.
            return False

        # Traverse nested modules or attributes
        for part in parts[1:]:
            if hasattr(module, part):
                module = getattr(module, part)
            else:
                return False

        return True

    except ImportError:
        return False


def validate_imports(import_list: List[str], library_name: str) -> Dict[str, bool]:
    """
    Validate the existence of multiple imports within a given library.

    Args:
        import_list (List[str]): A list of import paths to validate.
        library_name (str): The name of the library against which to validate the imports.

    Returns:
        Dict[str, bool]: A dictionary with import paths as keys and boolean values indicating
                         if the import exists within the specified library.

    Example usage:
        import_names = ['langchain.llms', 'langchain.prompts', 'langchain.LLMChain', 'langchain.agents']
        validate_imports(import_list=import_names, library_name='langchain')
        output: {'langchain.llms': True, 'langchain.prompts': True, 'langchain.LLMChain': True, 'langchain.agents': True}
    """
    result = {}
    for import_name in import_list:
        exists = check_import_exists(library_name, import_name)
        result[import_name] = exists
    return result


if __name__ == "__main__":
    """
    Can run from cli using:
    python check_import_existence.py '["langchain.llms", "langchain.prompts", "langchain.LLMChain", "langchain.agents"]' langchain
    """
    json_imports = sys.argv[1]
    import_names = json.loads(json_imports)
    library_name = sys.argv[2]
    import_env_validation_result = validate_imports(
        import_list=import_names, library_name="langchain"
    )
    print(json.dumps(import_env_validation_result))
