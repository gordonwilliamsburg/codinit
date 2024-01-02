from apify_client import ApifyClient
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
def mock_apify_client(mocker):
    mock_client = mocker.MagicMock(spec=ApifyClient)
    return mock_client
