from apify_client import ApifyClient
from codinit.config import DocumentationSettings, Secrets
from codinit.documentation.pydantic_models import Library
from codinit.documentation.pydantic_models import WebScrapingData, Metadata, Crawl
import pytest

@pytest.fixture
def mock_library():
    libname = "langchain"
    links = [
        "https://langchain-langchain.vercel.app/docs/get_started/",
        "https://python.langchain.com/docs/modules/",
    ]
    library = Library(libname=libname, links=links)
    return library

# fixture creates a sample WebScrapingData object for use in the test.
@pytest.fixture
def sample_data():
    return [
        WebScrapingData(
            url="https://example.com",
            text="Example text",
            metadata=Metadata(
                canonicalUrl="https://example.com",
                title="Example Title",
                description="Example Description",
                author="Author Name",
                keywords="keywords",
                languageCode="en",
            ),
            crawl=Crawl(
                loadedUrl="https://example.com",
                loadedTime="2021-01-01T00:00:00Z",
                referrerUrl="https://referrer.com",
                depth=1,
            ),
            screenshotUrl="https://example.com/screenshot.png",
            html="<html></html>",
            markdown="## Example Markdown",
        )
    ]


@pytest.fixture
def mock_secrets():
    # Create a Secrets instance with test values
    return Secrets(
        openai_api_key="test_key",
        huggingface_key="test_key",
        persist_dir="test_dir",
        model_path="test_model_path",
        repo_path="test_repo_path",
        docs_dir="test_docs_dir",
        weaviate_url="http://test_weaviate_url:8080",
        apify_key="test_apify_key"
    )

@pytest.fixture
def mock_documentation_settings():
    # Create a DocumentationSettings instance with test values
    return DocumentationSettings(
        chunk_size=100,
        overlap=10,
        top_k=5,
        alpha=0.5
    )

@pytest.fixture
def mock_apify_client(mocker):
    mock_client = mocker.MagicMock(spec=ApifyClient)
    return mock_client
