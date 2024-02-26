import logging
from typing import List

import weaviate.classes as wvc

from codinit.weaviate_client import get_weaviate_client

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_files(prompt: str, k: int = 1) -> str:
    """Returns code file relevant for a given prompt
    Args:
        prompt: str, description of the file to search for.
        k: int, the number of most similar files to the prompt to be returned by the query.
    """
    client = get_weaviate_client()
    client.connect()
    file_collection = client.collections.get("File")
    result = file_collection.query.near_text(
        query=prompt,
        return_properties=["name"],
        return_references=[
            wvc.query.QueryReference(link_on="hasImport", return_properties=["name"]),
            wvc.query.QueryReference(link_on="hasClass", return_properties=["name"]),
            wvc.query.QueryReference(link_on="hasFunction", return_properties=["name"]),
        ],
        limit=k,
    )
    client.close()
    files = result.objects
    logging.info(f"file objects query {files=}")
    query_result = "found the following files: "
    for file in files:
        query_result += f'\n file {file.properties["name"]}, '
        try:
            query_result += f'has imports: {[object.properties["name"] for object in file.references["hasImport"].objects]}, '
        except KeyError:
            pass
        try:
            query_result += f'has classes named: {[object.properties["name"] for object in file.references["hasClass"].objects]}, '
        except KeyError:
            pass
        try:
            query_result += f'has functions named: {[object.properties["name"] for object in file.references["hasFunction"].objects]}'
        except KeyError:
            pass
    logging.debug(f"files query_result {query_result=}")
    return query_result


def get_classes(prompt: str, k: int = 1) -> str:
    """Returns code classes relevant for a given prompt
    Args:
        prompt: str, description of the class to search for.
        k: int, the number of most similar classes to the prompt to be returned by the query.
    """
    client = get_weaviate_client()
    client.connect()
    class_collection = client.collections.get("Class")
    result = class_collection.query.near_text(
        query=prompt,
        return_properties=["name"],
        return_references=[
            wvc.query.QueryReference(link_on="hasFunction", return_properties=["name"])
        ],
        limit=k,
    )
    client.close()
    classes = result.objects
    logging.info(f"class objects query{classes=}")
    query_result = "found the following classes: "
    for class_ in classes:
        query_result += f'\n class with name: {class_.properties["name"]} '
        try:
            query_result += f'has functions: {[object.properties["name"] for object in class_.references["hasFunction"].objects]}'
        except KeyError:
            pass
    logging.debug(f"classes query_result {query_result=}")
    return query_result


def get_imports(prompt: str, k: int = 1) -> str:
    """Returns code imports relevant for a given prompt
    Args:
        prompt: str, description of the import to search for.
        k: int, the number of most similar imports to the prompt to be returned by the query.
    """
    client = get_weaviate_client()
    client.connect()
    import_collection = client.collections.get("Import")
    result = import_collection.query.near_text(
        query=prompt,
        return_properties=["name"],
        return_references=[
            wvc.query.QueryReference(
                link_on="belongsToFile", return_properties=["name"]
            )
        ],
        limit=k,
    )
    client.close()
    imports = result.objects
    logging.info(f"import bjects query{imports=}")
    query_result = "found the following imports:"
    for import_ in imports:
        query_result += f'\n import name: {import_.properties["name"]} '
        try:
            query_result += f'belongs to file: {[object.properties["name"] for object in import_.references["belongsToFile"].objects]}'
        except KeyError:
            pass
    logging.debug(f"imports query_result {query_result=}")
    return query_result


def get_functions(prompt: str, k: int = 1) -> str:
    """Returns code functions relevant for a given prompt
    Args:
        prompt: str, description of the function to search for.
        k: int, the number of most similar functions to the prompt to be returned by the query.
    """
    client = get_weaviate_client()
    client.connect()
    function_collection = client.collections.get("Function")
    result = function_collection.query.near_text(
        query=prompt,
        return_properties=["name", "code", "parameters", "variables", "return_value"],
        return_references=[
            wvc.query.QueryReference(
                link_on="belongsToFile", return_properties=["name"]
            ),
            wvc.query.QueryReference(
                link_on="belongsToClass", return_properties=["name"]
            ),
        ],
        limit=k,
    )
    client.close()
    functions = result.objects
    logging.info(f"function objects query{functions=}")
    query_result = "found the following functions: "
    for function in functions:
        query_result += f'\n function named: {function.properties["name"]} '
        try:
            query_result += f'belongs to file: {[object.properties["name"] for object in function.references["belongsToFile"].objects]}'
        except KeyError:
            pass
        try:
            query_result += f'belongs to class: {[object.properties["name"] for object in function.references["belongsToClass"].objects]}'
        except KeyError:
            pass
    logging.debug(f"functions query_result {query_result=}")
    return query_result


def get_exact_imports(query: str, k: int = 1) -> str:
    """Returns exact imports relevant for a given prompt"""
    client = get_weaviate_client()
    client.connect()
    import_collection = client.collections.get("Import")
    result = import_collection.query.bm25(query=query, properties=["name"], limit=k)
    client.close()
    return result.objects


def get_imports_from_kg(import_list: List[str], library_name: str, k=10):
    """Returns exact imports relevant for a given prompt"""

    result = {}
    for import_name in import_list:
        exists_in_weaviate_kg = get_exact_imports(query=import_name, k=k)
        result[import_name] = exists_in_weaviate_kg
    return result


if __name__ == "__main__":
    # get_classes("Agent")
    # get_imports("Agent")
    get_functions("execute", k=4)
    # get_files("agent.py")
