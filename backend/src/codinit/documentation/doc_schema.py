library_class = {
    "class": "Library",
    "description": "A code library",
    "vectorizer": "text2vec-openai",
    "moduleConfig": {
        "text2vec-openai": {"model": "ada", "modelVersion": "002", "type": "text"}
    },
    "properties": [
        {"name": "name", "dataType": ["text"]},
        {"name": "links", "dataType": ["text[]"]},
        {"name": "description", "dataType": ["text"]},
        {
            "name": "hasDocumentationFile",
            "dataType": ["DocumentationFile"],
            "description": "Documentation of the library",
        },
    ],
}

documentation_file_class = {
    "class": "DocumentationFile",
    "description": "A documentation file of a library",
    "vectorizer": "text2vec-openai",
    "moduleConfig": {
        "text2vec-openai": {"model": "ada", "modelVersion": "002", "type": "text"}
    },
    "properties": [
        {
            "name": "title",
            "dataType": ["text"],
            "description": "title of the document",
        },
        {
            "name": "description",
            "dataType": ["text"],
            "description": "Description of the content of the documentation file",
        },
        {
            "name": "chunknumber",
            "dataType": ["int"],
            "description": "Order of the chunk in the original documentation file",
        },
        {
            "name": "source",
            "dataType": ["text"],
            "description": "URL source of the documentation file",
        },
        {
            "name": "language",
            "dataType": ["text"],
            "description": "Language of the documentation file",
        },
        {
            "name": "content",
            "dataType": ["text"],
            "description": "Content of the documentation file",
        },
        {
            "name": "fromLibrary",
            "dataType": ["Library"],
            "description": "The library the documentation belongs to",
        },
    ],
}

if __name__ == "__main__":
    from codinit.weaviate_client import get_weaviate_client

    client = get_weaviate_client()

    client.schema.delete_class("Library")
    client.schema.delete_class("DocumentationFile")
    client.schema.create({"classes": [library_class, documentation_file_class]})
