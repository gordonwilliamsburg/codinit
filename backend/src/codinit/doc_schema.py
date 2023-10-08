from codinit.config import client

library_class = {
    "class": "Library",
    "description": "A code library",
    "vectorizer": "text2vec-huggingface",
    "moduleConfig": {
        "text2vec-huggingface": {
            "vectorizeClassName": True,
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "options": {"waitForModel": True},
        }
    },
    "properties": [
        {"name": "name", "dataType": ["text"]},
        {"name": "links", "dataType": ["text[]"]},
        {"name": "description", "dataType": ["text"]},
        {
            "name": "hasDocumentionFile",
            "dataType": ["DocumentionFile"],
            "description": "Documentation of the library",
        },
    ],
}

documentation_file_class = {
    "class": "DocumentionFile",
    "description": "A documentation file of a library",
    "vectorizer": "text2vec-huggingface",
    "moduleConfig": {
        "text2vec-huggingface": {
            "vectorizeClassName": True,
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "options": {"waitForModel": True},
        }
    },
    "properties": [
        {
            "name": "title",
            "dataType": ["text"],
            "description": "The name of the author",
        },
        {
            "name": "description",
            "dataType": ["text"],
            "description": "Description of the content of the documentation file",
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
client.schema.delete_class("Library")
client.schema.delete_class("DocumentionFile")
client.schema.create({"classes": [library_class, documentation_file_class]})
