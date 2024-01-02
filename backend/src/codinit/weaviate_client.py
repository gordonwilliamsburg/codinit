import weaviate
from weaviate.embedded import EmbeddedOptions

from codinit.config import secrets


# Create Weaviate client
def get_weaviate_client():
    # Create Weaviate client
    client = weaviate.Client(
        embedded_options=EmbeddedOptions(
            port=5001,
            persistence_data_path=secrets.persist_dir,
            additional_env_vars={
                "ENABLE_MODULES": "text2vec-openai,text2vec-cohere,text2vec-huggingface,ref2vec-centroid,generative-openai,qna-openai"
            },
        ),
        additional_headers={
            "X-HuggingFace-Api-Key": secrets.huggingface_key,
            "X-OpenAI-Api-Key": secrets.openai_api_key,
        },
    )
    return client
