import weaviate
import weaviate.classes.config as wvcc

from codinit.weaviate_utils import get_collection_references


def create_library_schema(client: weaviate.WeaviateClient):
    client.connect()
    try:
        # Create the Library collection
        library_collection = client.collections.create(
            name="Library",
            vectorizer_config=wvcc.Configure.Vectorizer.text2vec_openai(
                model="ada", model_version="002"
            ),
            properties=[
                wvcc.Property(name="name", data_type=wvcc.DataType.TEXT),
                wvcc.Property(name="links", data_type=wvcc.DataType.TEXT_ARRAY),
                wvcc.Property(name="description", data_type=wvcc.DataType.TEXT),
            ],
        )
    finally:
        client.close()
    return library_collection


def create_documentation_schema(client: weaviate.WeaviateClient):
    client.connect()
    try:
        # Create the DocumentationFile collection
        documentation_file_collection = client.collections.create(
            name="DocumentationFile",
            vectorizer_config=wvcc.Configure.Vectorizer.text2vec_openai(
                model="ada", model_version="002"
            ),
            properties=[
                wvcc.Property(
                    name="title",
                    data_type=wvcc.DataType.TEXT,
                    description="title of the document",
                ),
                wvcc.Property(
                    name="description",
                    data_type=wvcc.DataType.TEXT,
                    description="Description of the content of the documentation file",
                ),
                wvcc.Property(
                    name="chunknumber",
                    data_type=wvcc.DataType.INT,
                    description="Order of the chunk in the original documentation file",
                ),
                wvcc.Property(
                    name="source",
                    data_type=wvcc.DataType.TEXT,
                    description="URL source of the documentation file",
                ),
                wvcc.Property(
                    name="language",
                    data_type=wvcc.DataType.TEXT,
                    description="Language of the documentation file",
                ),
                wvcc.Property(
                    name="content",
                    data_type=wvcc.DataType.TEXT,
                    description="Content of the documentation file",
                ),
            ],
        )
    finally:
        client.close()
    return documentation_file_collection


def create_doc_library_schema(client: weaviate.WeaviateClient):
    client.connect()
    try:
        collections = client.collections.list_all()
        collection_names = set(collections.keys())

        if "Library" not in collection_names:
            create_library_schema(client)
        if "DocumentationFile" not in collection_names:
            create_documentation_schema(client)
    finally:
        client.close()


# Create the schema
def add_documentation_schema_references(client: weaviate.WeaviateClient):
    client.connect()

    try:
        library_collection = client.collections.get("Library")
        library_references = get_collection_references(collection=library_collection)
        if "hasDocumentationFile" not in library_references:
            library_collection.config.add_reference(
                ref=wvcc.ReferenceProperty(
                    name="hasDocumentationFile",
                    target_collection="DocumentationFile",
                    description="Documentation of the library",
                )
            )

        documentation_file_collection = client.collections.get("DocumentationFile")
        documentation_file_references = get_collection_references(
            collection=documentation_file_collection
        )
        if "fromLibrary" not in documentation_file_references:
            documentation_file_collection.config.add_reference(
                ref=wvcc.ReferenceProperty(
                    name="fromLibrary",
                    target_collection="Library",
                    description="The library the documentation belongs to",
                )
            )
    finally:
        client.close()
    return library_collection, documentation_file_collection


def init_library_schema_weaviate(client: weaviate.WeaviateClient):
    client.connect()

    try:
        create_doc_library_schema(client)
        add_documentation_schema_references(client)
    finally:
        client.close()


# Create the schema
if __name__ == "__main__":
    from codinit.weaviate_client import get_weaviate_client

    client = get_weaviate_client()
    init_library_schema_weaviate(client)
