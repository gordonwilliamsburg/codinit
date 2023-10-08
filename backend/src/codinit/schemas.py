from codinit.config import client

# define knowledge graph schema
schema = {
    "classes": [
        {
            "class": "Repository",
            "description": "A code repository",
            "vectorizer": "text2vec-huggingface",
            "vectorIndexType": "hnsw",
            "moduleConfig": {
                "text2vec-huggingface": {
                    "vectorizeClassName": True,
                    "model": "sentence-transformers/all-MiniLM-L6-v2",
                    "options": {"waitForModel": True},
                }
            },
            "properties": [
                {
                    "name": "name",
                    "dataType": ["text"],
                    "description": "name of the repository",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": True,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
                {
                    "name": "link",
                    "dataType": ["text"],
                    "description": "URL link to the remote repository",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": True,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
                {
                    "name": "hasFile",
                    "dataType": ["File"],
                    "description": "Files contained in the repository",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": True,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
            ],
        },
        {
            "class": "File",
            "description": "A file in a repository",
            "vectorizer": "text2vec-huggingface",
            "vectorIndexType": "hnsw",
            "moduleConfig": {
                "text2vec-huggingface": {
                    "vectorizeClassName": True,
                    "model": "sentence-transformers/all-MiniLM-L6-v2",
                    "options": {"waitForModel": True},
                }
            },
            "properties": [
                {
                    "name": "name",
                    "dataType": ["text"],
                    "description": "Name of the file",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": False,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
                {
                    "name": "link",
                    "dataType": ["text"],
                    "description": "Full link of the file in the remote repository",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": True,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
                {
                    "name": "description",
                    "dataType": ["text"],
                    "description": "An LLM generated description of the file",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": False,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
                {
                    "name": "hasImport",
                    "dataType": ["Import"],
                    "description": "Imports in the file",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": False,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
                {
                    "name": "hasClass",
                    "dataType": ["Class"],
                    "description": "Classes defined in the file",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": False,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
                {
                    "name": "hasFunction",
                    "dataType": ["Function"],
                    "description": "Functions defined in the file",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": False,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
            ],
        },
        {
            "class": "Import",
            "description": "An import in a file",
            "vectorizer": "text2vec-huggingface",
            "vectorIndexType": "hnsw",
            "moduleConfig": {
                "text2vec-huggingface": {
                    "vectorizeClassName": True,
                    "model": "sentence-transformers/all-MiniLM-L6-v2",
                    "options": {"waitForModel": True},
                }
            },
            "properties": [
                {
                    "name": "name",
                    "dataType": ["text"],
                    "description": "Name of the import",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": False,
                            "vectorizePropertyName": True,
                            "vectorizeClassName": True,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
                {
                    "name": "belongsToFile",
                    "dataType": ["File"],
                    "description": "File the import is located in",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": False,
                            "vectorizePropertyName": True,
                            "vectorizeClassName": True,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
            ],
        },
        {
            "class": "Class",
            "description": "A class in a file",
            "vectorizer": "text2vec-huggingface",
            "vectorIndexType": "hnsw",
            "moduleConfig": {
                "text2vec-huggingface": {
                    "vectorizeClassName": True,
                    "model": "sentence-transformers/all-MiniLM-L6-v2",
                    "options": {"waitForModel": True},
                }
            },
            "properties": [
                {
                    "name": "name",
                    "dataType": ["text"],
                    "description": "Name of the class",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": False,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
                {
                    "name": "description",
                    "dataType": ["text"],
                    "description": "An LLM generated description of the class",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": False,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
                {
                    "name": "attributes",
                    "dataType": ["text[]"],
                    "description": "attributes of the class",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": True,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
                {
                    "name": "hasFunction",
                    "dataType": ["Function"],
                    "description": "Functions defined in the class",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": True,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
                {
                    "name": "belongsToFile",
                    "dataType": ["File"],
                    "description": "File the class is defined in",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": True,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
            ],
        },
        {
            "class": "Function",
            "description": "A function in a file or class",
            "vectorizer": "text2vec-huggingface",
            "vectorIndexType": "hnsw",
            "moduleConfig": {
                "text2vec-huggingface": {
                    "vectorizeClassName": True,
                    "model": "sentence-transformers/all-MiniLM-L6-v2",
                    "options": {"waitForModel": True},
                }
            },
            "properties": [
                {
                    "name": "name",
                    "dataType": ["text"],
                    "description": "Name of the function",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": True,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
                {
                    "name": "description",
                    "dataType": ["text"],
                    "description": "An LLM generated description of the function",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": False,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
                {
                    "name": "code",
                    "dataType": ["text"],
                    "description": "Code body of the function",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": True,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
                {
                    "name": "parameters",
                    "dataType": ["text[]"],
                    "description": "Parameters of the function",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": True,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
                {
                    "name": "variables",
                    "dataType": ["text[]"],
                    "description": "Variables used in the function",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": True,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
                {
                    "name": "return_value",
                    "dataType": ["text[]"],
                    "description": "Return values of the function",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": True,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
                {
                    "name": "belongsToFile",
                    "dataType": ["File"],
                    "description": "File the function is defined in",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": True,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
                {
                    "name": "belongsToClass",
                    "dataType": ["Class"],
                    "description": "Class the function is part of",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": True,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False,
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                            "options": {"waitForModel": True},
                        }
                    },
                },
            ],
        },
    ]
}

import_class_schema = {
    "class": "Import",
    "description": "An import in a file",
    "vectorizer": "text2vec-huggingface",
    "vectorIndexType": "hnsw",
    "moduleConfig": {
        "text2vec-huggingface": {
            "vectorizeClassName": True,
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "options": {"waitForModel": True},
        }
    },
    "properties": [
        {
            "name": "name",
            "dataType": ["text"],
            "description": "Name of the import",
            "moduleConfig": {
                "text2vec-huggingface": {
                    "skip": False,
                    "vectorizePropertyName": True,
                    "vectorizeClassName": True,
                    "model": "sentence-transformers/all-MiniLM-L6-v2",
                    "options": {"waitForModel": True},
                }
            },
        },
        {
            "name": "belongsToFile",
            "dataType": ["File"],
            "description": "File the import is located in",
            "moduleConfig": {
                "text2vec-huggingface": {
                    "skip": False,
                    "vectorizePropertyName": True,
                    "vectorizeClassName": True,
                    "model": "sentence-transformers/all-MiniLM-L6-v2",
                    "options": {"waitForModel": True},
                }
            },
        },
    ],
}
# create schema
client.schema.delete_class("Repository")
client.schema.delete_class("File")
client.schema.delete_class("Class")
client.schema.delete_class("Function")
client.schema.delete_class("Import")
client.schema.create(schema=schema)
# client.schema.create_class(import_class_schema)
