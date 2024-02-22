import weaviate
import weaviate.classes.config as wvcc

from codinit.weaviate_client import get_weaviate_client
from codinit.weaviate_utils import get_collection_references


def create_repository_collection(client: weaviate.WeaviateClient):
    client.connect()
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
    finally:
        client.close()
    return repository_collection


def create_file_collection(client: weaviate.WeaviateClient):
    client.connect()
    try:
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
    finally:
        client.close()
    return file_collection


def create_import_collection(client: weaviate.WeaviateClient):
    client.connect()
    try:
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
    finally:
        client.close()
    return import_collection


def create_class_collection(client: weaviate.WeaviateClient):
    client.connect()
    try:
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
    finally:
        client.close()
    return class_collection


def create_function_collection(client: weaviate.WeaviateClient):
    client.connect()
    try:
        # Create the Function collection
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
    finally:
        client.close()
    return function_collection


def create_kg_collections(client: weaviate.WeaviateClient):
    client.connect()
    try:
        collections = client.collections.list_all()
        collection_names = set(collections.keys())

        if "Repository" not in collection_names:
            create_repository_collection(client)
        if "File" not in collection_names:
            create_file_collection(client)
        if "Import" not in collection_names:
            create_import_collection(client)
        if "Class" not in collection_names:
            create_class_collection(client)
        if "Function" not in collection_names:
            create_function_collection(client)
    finally:
        client.close()


def add_kg_schema_references(client: weaviate.WeaviateClient):
    client.connect()
    try:
        # Add the reference property to the Repository collection
        repository_collection = client.collections.get("Repository")
        repository_references = get_collection_references(
            collection=repository_collection
        )
        if "hasFile" not in repository_references:
            repository_collection.config.add_reference(
                ref=wvcc.ReferenceProperty(
                    name="hasFile",
                    target_collection="File",
                    description="Files contained in the repository",
                )
            )

        # Add reference properties to the File collection
        file_collection = client.collections.get("File")
        file_references = get_collection_references(collection=file_collection)
        for reference in ["hasImport", "hasClass", "hasFunction"]:
            if reference not in file_references:
                file_collection.config.add_reference(
                    ref=wvcc.ReferenceProperty(
                        name=reference,
                        target_collection=reference[
                            3:
                        ],  # Assuming collection names are "Import", "Class", "Function"
                        description=f"{reference[3:]}s defined in the file",
                    )
                )

        # Add reference properties to the Import collection
        import_collection = client.collections.get("Import")
        import_references = get_collection_references(collection=import_collection)
        if "belongsToFile" not in import_references:
            import_collection.config.add_reference(
                ref=wvcc.ReferenceProperty(
                    name="belongsToFile",
                    target_collection="File",
                    description="File the import is located in",
                )
            )

        # Add reference properties to the Class collection
        class_collection = client.collections.get("Class")
        class_references = get_collection_references(collection=class_collection)
        if "hasFunction" not in class_references:
            class_collection.config.add_reference(
                ref=wvcc.ReferenceProperty(
                    name="hasFunction",
                    target_collection="Function",
                    description="reference property for functions contained in a class",
                )
            )
        if "belongsToFile" not in class_references:
            class_collection.config.add_reference(
                ref=wvcc.ReferenceProperty(
                    name="belongsToFile",
                    target_collection="File",
                    description="reference property for the file that contains the class",
                )
            )

        # Add reference properties to the Function collection
        function_collection = client.collections.get("Function")
        function_references = get_collection_references(collection=function_collection)
        if "belongsToFile" not in function_references:
            function_collection.config.add_reference(
                ref=wvcc.ReferenceProperty(
                    name="belongsToFile",
                    target_collection="File",
                    description="reference property for the file that contains the function",
                )
            )
        if "belongsToClass" not in function_references:
            function_collection.config.add_reference(
                ref=wvcc.ReferenceProperty(
                    name="belongsToClass",
                    target_collection="Class",
                    description="reference property for the class that contains the function",
                )
            )

    finally:
        client.close()


def init_code_kg_schema_weaviate(client: weaviate.WeaviateClient):
    client.connect()

    try:
        create_kg_collections(client)
        add_kg_schema_references(client)
    finally:
        client.close()


if __name__ == "__main__":
    client = get_weaviate_client()

    client.collections.delete("Repository")
    client.collections.delete("File")
    client.collections.delete("Import")
    client.collections.delete("Class")
    client.collections.delete("Function")
    init_code_kg_schema_weaviate(client)
