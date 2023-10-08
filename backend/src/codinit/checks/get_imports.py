from typing import List, Optional, Tuple

import libcst as cst
import libcst.metadata as metadata


class LibraryUsageVisitor(cst.CSTVisitor):
    """
    Custom CST visitor class to extract usages of library_name in the code.
    """

    def __init__(self, library_name: str):
        """
        Initialize the visitor with an empty list to store discovered usages.
        """
        self.used_names: List[str] = []
        self.library_name = library_name

    def _handle_name_usage(self, name_node: cst.CSTNode) -> Optional[str]:
        """
        Helper function to extract the full path of the name if it is
        a usage from library_name.

        Parameters:
        - name_node: The node to check for library_name usage.

        Returns:
        - A string representing the full path if it's a library_name usage,
          otherwise None.
        """

        # Handle usage of names in the format "library_name.X"
        if isinstance(name_node, cst.Attribute):
            base_name = self._handle_name_usage(name_node.value)
            if base_name:
                return f"{base_name}.{name_node.attr.value}"
        elif isinstance(name_node, cst.Name) and name_node.value == self.library_name:
            return name_node.value
        return None

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        """
        Overridden visit method to capture ImportFrom nodes.

        Parameters:
        - node: The ImportFrom node being visited.
        """
        if not node.module:
            return

        module_name = node.module.value

        if module_name == self.library_name or module_name.startswith(
            self.library_name + "."
        ):
            for name_item in node.names:
                if isinstance(name_item, cst.ImportAlias) and hasattr(
                    name_item.name, "value"
                ):
                    imported_name = name_item.name.value
                    self.used_names.append(f"{module_name}.{imported_name}")

    def visit_Attribute(self, node: cst.Attribute) -> None:
        """
        Overridden visit method to capture Attribute nodes.

        Parameters:
        - node: The Attribute node being visited.
        """

        name_usage = self._handle_name_usage(node)
        if name_usage:
            self.used_names.append(name_usage)


def extract_library_usages(code: str, library_name: str) -> list:
    """
    Parses the provided code and extracts all usages of library_name.

    Parameters:
    - code: A string containing the code to analyze.

    Returns:
    - A list of str, where each str contains the library_name
      usage path.
    """

    # Wrap the parsed module with metadata.
    wrapper = cst.MetadataWrapper(cst.parse_module(code))

    # Create an instance of the custom visitor and visit the wrapped CST.
    visitor = LibraryUsageVisitor(library_name=library_name)
    wrapper.visit(visitor)

    return visitor.used_names


if __name__ == "__main__":
    original_code = "src/codinit/checks/sample_code/sample_code.py"
    processed_code = "src/codinit/checks/sample_code/sample_corrected_code.py"
    with open(processed_code, "r") as file:
        code = file.read()
    names = extract_library_usages(code, library_name="langchain")
    print(names)
