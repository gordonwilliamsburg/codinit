import logging

import weaviate
from weaviate.exceptions import WeaviateStartUpError

from codinit.config import secrets

# Configure logging at the start of your program
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# Create Weaviate client
def get_weaviate_client() -> weaviate.WeaviateClient:
    try:
        # Create Weaviate client
        # use context manager to avoid resource leaks and warnings
        with weaviate.connect_to_embedded(
            port=5001,
            persistence_data_path=secrets.persist_dir,
            environment_variables={
                "ENABLE_MODULES": "text2vec-openai,text2vec-cohere,text2vec-huggingface,ref2vec-centroid,generative-openai,qna-openai"
            },
            headers={
                "X-HuggingFace-Api-Key": secrets.huggingface_key,
                "X-OpenAI-Api-Key": secrets.openai_api_key,
            },
        ) as client:
            return client
    except WeaviateStartUpError as e:
        logging.error(f"Error starting Weaviate: {e}, connecting to local")
        return weaviate.connect_to_local(port=5001, grpc_port=50050)

    return client


if __name__ == "__main__":
    client = get_weaviate_client()
    print(client.collections.list_all())
    client.close()
