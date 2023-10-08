import ast
import importlib
import json
import keyword
import sys
from typing import Dict, Optional, Set, Tuple


class ReferenceCollector(ast.NodeVisitor):
    def __init__(self):
        # Set to store references found in the code
        self.references: Set[Tuple[Optional[str], str]] = set()

    def _get_full_name(self, node: ast.AST) -> Tuple[Optional[str], str]:
        """
        Recursively retrieves the full name of an AST node.

        Returns:
            Tuple where the first element represents the parent (or None if no parent) and
            the second element represents the actual attribute or name.
        """
        if isinstance(node, ast.Name):
            return None, node.id
        elif isinstance(node, ast.Attribute):
            parent, base = self._get_full_name(node.value)
            return (base if parent is None else f"{parent}.{base}", node.attr)
        return None, ""

    def visit_Attribute(self, node: ast.Attribute):
        """
        Extracts attributes from the code being parsed.
        """
        parent, name = self._get_full_name(node)
        if name:
            self.references.add((parent, name))
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """
        Extracts function or class names from the code being parsed.
        """
        parent, name = self._get_full_name(node.func)
        if name:
            self.references.add((parent, name))
        self.generic_visit(node)


def validate_reference(parent: Optional[str], attr: str, module: object) -> bool:
    """
    Validates if a reference (attribute) exists in the given module or its parent.
    """
    if parent:
        parts = parent.split(".")
        for part in parts:
            if hasattr(module, part):
                module = getattr(module, part)
            else:
                return False

    return hasattr(module, attr)


def validate_references(
    references: Set[Tuple[Optional[str], str]], module_name: str
) -> Dict[str, bool]:
    """
    Validates a set of references against a given module.

    Returns:
        Dictionary where keys are the references and values indicate whether the reference exists in the module.
    """
    module = importlib.import_module(module_name)
    results = {}
    for parent, attr in references:
        if attr not in dir(__builtins__) and not keyword.iskeyword(attr):
            full_ref = f"{parent}.{attr}" if parent else attr
            print(full_ref)
            exists = validate_reference(parent, attr, module)
            results[full_ref] = exists
    return results


def check_references_code(code: str, library_name: str) -> Dict[str, bool]:
    """
    Checks the code for references and validates them against the given library name.

    Returns:
        Dictionary where keys are the references and values indicate whether the reference exists in the library.
    """
    node = ast.parse(code)
    collector = ReferenceCollector()
    collector.visit(node)
    return validate_references(collector.references, library_name)


if __name__ == "__main__":
    code_path = sys.argv[1]
    library_name = sys.argv[2]

    with open(code_path, "r") as file:
        code = file.read()

    reference_results = check_references_code(code=code, library_name=library_name)
    print(json.dumps(reference_results))
