import weaviate
import weaviate.classes.config as wvcc


def create_documentation_schema(client: weaviate.WeaviateClient):
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

        library_collection.config.add_reference(
            ref=wvcc.ReferenceProperty(
                name="hasDocumentationFile",
                target_collection="DocumentationFile",
                description="Documentation of the library",
            )
        )

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


# Create the schema
if __name__ == "__main__":
    from codinit.weaviate_client import get_weaviate_client

    client = get_weaviate_client()
    client.collections.delete_all()
    library_class, documentation_file_class = create_documentation_schema(client)
