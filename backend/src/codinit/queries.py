from typing import List

import weaviate

from codinit.weaviate_client import get_weaviate_client


def get_files(prompt: str, client: weaviate.Client, k: int = 1):
    """Returns code file relevant for a given prompt
    Args:
        prompt: str, description of the file to search for.
        k: int, the number of most similar files to the prompt to be returned by the query.
    """
    result = (
        client.query.get(
            "File",
            properties=[
                "name",
                "hasImport {... on Import {name}}",
                "hasClass {... on Class {name}}",
                "hasFunction {... on Function {name}}",
            ],
        )
        .with_near_text({"concepts": [prompt]})
        .with_limit(k)
        .do()
    )
    return result["data"]["Get"]["File"]


def get_classes(prompt: str, client: weaviate.Client, k: int = 1):
    """Returns code classes relevant for a given prompt
    Args:
        prompt: str, description of the class to search for.
        k: int, the number of most similar classes to the prompt to be returned by the query.
    """
    result = (
        client.query.get(
            "Class",
            properties=["name", "attributes", "hasFunction {... on Function {name}}"],
        )
        .with_near_text({"concepts": [prompt]})
        .with_limit(k)
        .do()
    )
    return result["data"]["Get"]["Class"]


def get_imports(prompt: str, client: weaviate.Client, k: int = 1):
    """Returns code imports relevant for a given prompt
    Args:
        prompt: str, description of the import to search for.
        k: int, the number of most similar imports to the prompt to be returned by the query.
    """
    result = (
        client.query.get(
            "Import",
            properties=["name", "belongsToFile {... on File {name}}"],
        )
        .with_near_text({"concepts": [prompt]})
        .with_limit(k)
        .do()
    )
    return result["data"]["Get"]["Import"]


def get_functions(prompt: str, client: weaviate.Client, k: int = 1):
    """Returns code functions relevant for a given prompt
    Args:
        prompt: str, description of the function to search for.
        k: int, the number of most similar functions to the prompt to be returned by the query.
    """
    result = (
        client.query.get(
            "Function",
            properties=[
                "name",
                "code",
                "parameters",
                "variables",
                "return_value",
                "belongsToFile {... on File {name}}",
                "belongsToClass {... on Class {name}}",
            ],
        )
        .with_near_text({"concepts": [prompt]})
        .with_limit(k)
        .do()
    )
    return result["data"]["Get"]["Function"]


def get_exact_imports(query: str, client: weaviate.Client, k: int = 1):
    """Returns exact imports relevant for a given prompt"""
    result = (
        client.query.get(
            "Import",
            properties=["name"],
        )
        .with_bm25(query=query, properties=["name"])
        .with_limit(k)
        .do()
    )
    return result["data"]["Get"]["Import"]


def get_imports_from_kg(import_list: List[str], library_name: str, k=10):
    client = get_weaviate_client()

    result = {}
    for import_name in import_list:
        exists_in_weaviate_kg = get_exact_imports(query=import_name, client=client, k=k)
        result[import_name] = exists_in_weaviate_kg
    return result
