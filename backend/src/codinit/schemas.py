import weaviate
import weaviate.classes.config as wvcc

from codinit.weaviate_client import get_weaviate_client


def create_kg_schema(client: weaviate.WeaviateClient):
    try:
        # Create the Repository collection
        repository_collection = client.collections.create(
            name="Repository",
            vectorizer_config=wvcc.Configure.Vectorizer.text2vec_openai(
                model="ada", model_version="002"
            ),
            properties=[
                wvcc.Property(
                    name="name",
                    data_type=wvcc.DataType.TEXT,
                    description="name of the repository",
                ),
                wvcc.Property(
                    name="link",
                    data_type=wvcc.DataType.TEXT,
                    description="URL link to the remote repository",
                    skip_vectorization=True,
                ),
            ],
            vector_index_config=wvcc.Configure.VectorIndex.hnsw(),
        )

        # Create the File collection
        file_collection = client.collections.create(
            name="File",
            vectorizer_config=wvcc.Configure.Vectorizer.text2vec_openai(
                model="ada", model_version="002"
            ),
            properties=[
                wvcc.Property(
                    name="name",
                    data_type=wvcc.DataType.TEXT,
                    description="Name of the file",
                ),
                wvcc.Property(
                    name="link",
                    data_type=wvcc.DataType.TEXT,
                    description="Full link of the file in the remote repository",
                    skip_vectorization=True,
                ),
                wvcc.Property(
                    name="description",
                    data_type=wvcc.DataType.TEXT,
                    description="An LLM generated description of the file",
                )
                # Note: The reference properties will be added later
            ],
            vector_index_config=wvcc.Configure.VectorIndex.hnsw(),
        )

        # Create the Import collection
        import_collection = client.collections.create(
            name="Import",
            vectorizer_config=wvcc.Configure.Vectorizer.text2vec_openai(
                model="ada", model_version="002"
            ),
            properties=[
                wvcc.Property(
                    name="name",
                    data_type=wvcc.DataType.TEXT,
                    description="Name of the import",
                )
                # Note: The 'belongsToFile' property will be a reference and is added later
            ],
            vector_index_config=wvcc.Configure.VectorIndex.hnsw(),
        )

        # Create the Class collection
        class_collection = client.collections.create(
            name="Class",
            vectorizer_config=wvcc.Configure.Vectorizer.text2vec_openai(
                model="ada", model_version="002"
            ),
            properties=[
                wvcc.Property(
                    name="name",
                    data_type=wvcc.DataType.TEXT,
                    description="Name of the class",
                ),
                wvcc.Property(
                    name="description",
                    data_type=wvcc.DataType.TEXT,
                    description="An LLM generated description of the class",
                ),
                wvcc.Property(
                    name="attributes",
                    data_type=wvcc.DataType.TEXT_ARRAY,
                    description="attributes of the class",
                    skip_vectorization=True,
                )
                # Note: The reference properties will be added later
            ],
            vector_index_config=wvcc.Configure.VectorIndex.hnsw(),
        )

        # Create the Function collection without reference properties
        function_collection = client.collections.create(
            name="Function",
            vectorizer_config=wvcc.Configure.Vectorizer.text2vec_openai(
                model="ada", model_version="002"
            ),
            vector_index_config=wvcc.Configure.VectorIndex.hnsw(),
            properties=[
                wvcc.Property(
                    name="name",
                    data_type=wvcc.DataType.TEXT,
                    description="Name of the function",
                    skip_vectorization=True,
                ),
                wvcc.Property(
                    name="description",
                    data_type=wvcc.DataType.TEXT,
                    description="An LLM generated description of the function",
                ),
                wvcc.Property(
                    name="code",
                    data_type=wvcc.DataType.TEXT,
                    description="Code body of the function",
                    skip_vectorization=True,
                ),
                # Other properties as required
            ],
        )

        """
        Adding references
        """
        # Add the reference property to the Repository collection
        repository_collection.config.add_reference(
            ref=wvcc.ReferenceProperty(
                name="hasFile",
                target_collection="File",
                description="Files contained in the repository",
            )
        )

        # Add reference properties to the File collection
        for reference in ["hasImport", "hasClass", "hasFunction"]:
            file_collection.config.add_reference(
                ref=wvcc.ReferenceProperty(
                    name=reference,
                    target_collection=reference[
                        3:
                    ],  # Assuming collection names are "Import", "Class", "Function"
                    description=f"{reference[3:]}s defined in the file",
                )
            )

        # Add the reference property to the Import collection
        import_collection.config.add_reference(
            ref=wvcc.ReferenceProperty(
                name="belongsToFile",
                target_collection="File",
                description="File the import is located in",
            )
        )

        # Add 'hasFunction' reference property to the Class collection
        class_collection.config.add_reference(
            ref=wvcc.ReferenceProperty(
                name="hasFunction",
                target_collection="Function",
                description="Functions defined in the class",
            )
        )

        # Add 'belongsToFile' reference property to the Class collection
        class_collection.config.add_reference(
            ref=wvcc.ReferenceProperty(
                name="belongsToFile",
                target_collection="File",
                description="File the class is defined in",
            )
        )

        # Add function properties
        reference_properties = ["belongsToFile", "belongsToClass"]

        # Loop through each reference property and add it to the Function collection
        for reference in reference_properties:
            target_collection = (
                reference[9:] if reference.startswith("belongsTo") else reference
            )
            description = (
                f"{target_collection} the function is part of"
                if target_collection == "Class"
                else "File the function is defined in"
            )
            function_collection.config.add_reference(
                ref=wvcc.ReferenceProperty(
                    name=reference,
                    target_collection=target_collection,
                    description=description,
                )
            )
    finally:
        client.close()


if __name__ == "__main__":
    client = get_weaviate_client()

    client.collections.delete_all()
    create_kg_schema(client)
