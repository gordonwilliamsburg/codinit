import weaviate

from codinit.config import secrets


# Create Weaviate client
def get_weaviate_client() -> weaviate.WeaviateClient:
    # Create Weaviate client
    client = weaviate.connect_to_embedded(
        port=5001,
        persistence_data_path=secrets.persist_dir,
        environment_variables={
            "ENABLE_MODULES": "text2vec-openai,text2vec-cohere,text2vec-huggingface,ref2vec-centroid,generative-openai,qna-openai"
        },
        headers={
            "X-HuggingFace-Api-Key": secrets.huggingface_key,
            "X-OpenAI-Api-Key": secrets.openai_api_key,
        },
    )
    return client


if __name__ == "__main__":
    client = get_weaviate_client()
    print(client.collections.list_all())
    client.close()
