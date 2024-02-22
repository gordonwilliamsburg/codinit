from typing import List

import weaviate.classes as wvc

from codinit.weaviate_client import get_weaviate_client


def get_files(prompt: str, k: int = 1):
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
    return result.objects


def get_classes(prompt: str, k: int = 1):
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
    return result.objects


def get_imports(prompt: str, k: int = 1):
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
    return result.objects


def get_functions(prompt: str, k: int = 1):
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
    return result.objects


def get_exact_imports(query: str, k: int = 1):
    """Returns exact imports relevant for a given prompt"""
    client = get_weaviate_client()
    client.connect()
    import_collection = client.collections.get("Import")
    result = import_collection.query.bm25(query=query, properties=["name"], limit=k)
    client.close()
    return result["data"]["Get"]["Import"]


def get_imports_from_kg(import_list: List[str], library_name: str, k=10):
    """Returns exact imports relevant for a given prompt"""

    result = {}
    for import_name in import_list:
        exists_in_weaviate_kg = get_exact_imports(query=import_name, k=k)
        result[import_name] = exists_in_weaviate_kg
    return result
