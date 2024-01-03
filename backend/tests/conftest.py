from codinit.config import DocumentationSettings, Secrets
import pytest
import docker
import time
import weaviate
from weaviate import EmbeddedOptions
import shutil
import os

# Fixtures
@pytest.fixture(scope="session")
def mock_secrets():
    # Create a Secrets instance with test values
    return Secrets(_env_file='test.env', _env_file_encoding='utf-8')

@pytest.fixture
def mock_documentation_settings():
    # Create a DocumentationSettings instance with test values
    return DocumentationSettings(
        chunk_size=100,
        overlap=10,
        top_k=5,
        alpha=0.5
    )


# Weaviate instance fixture
# This fixture starts a Weaviate container in the background and provides a Weaviate client instance that can be used for testing
# set fixture scope to session to persist throughout the whole testinf session
# change scope to function if a fresh weaviate instance is needed for every test function
@pytest.fixture(scope="session")
def test_weaviate_client_docker():
    try:
        # Connect to Docker using DockerClient
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')  # or 'tcp://127.0.0.1:2375' for Windows or other setups

        # Start a Weaviate container in the background
        container = client.containers.run(
            "semitechnologies/weaviate:latest",
            detach=True,
            ports={'6364/tcp': 6364},
            remove=True
        )
        # Wait for Weaviate to be fully up and running
        time.sleep(30)  # Adjust the sleep time if necessary

        # Create a Weaviate client instance
        weaviate_client = weaviate.Client("http://localhost:6364")

        # Yield the Weaviate client instance to the test function
        yield weaviate_client

        # Teardown: stop the Weaviate container
        container.stop()
        # Remove the Weaviate container
        container.remove()
    # Handle any exceptions that may occur during the test run

    except docker.errors.DockerException as e:
        print(f"Error connecting to Docker: {e}")
        raise(e)


@pytest.fixture(scope="session")
def test_embedded_weaviate_client(mock_secrets):
    # Create an embedded Weaviate client
    client = weaviate.Client(
        embedded_options=EmbeddedOptions(
            persistence_data_path=mock_secrets.persist_dir,
            port= 8888,
            additional_env_vars={
                "ENABLE_MODULES": "text2vec-openai,text2vec-cohere,text2vec-huggingface,ref2vec-centroid,generative-openai,qna-openai"
            },
        ),
        additional_headers={
            "X-HuggingFace-Api-Key": mock_secrets.huggingface_key,
            "X-OpenAI-Api-Key": mock_secrets.openai_api_key,
        },
    )

    yield client

    # Teardown: the client is closed after app termination so we only need to clean up persistent data
    # Teardown: Clean up the data directory
    if os.path.exists(mock_secrets.persist_dir):
        shutil.rmtree(mock_secrets.persist_dir)
