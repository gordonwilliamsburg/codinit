def get_collection_references(collection):
    collection_configs = collection.config.get()
    collection_references = [
        reference.name for reference in collection_configs.references
    ]
    return collection_references
