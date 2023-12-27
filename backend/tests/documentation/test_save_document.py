import json
import pytest
from codinit.documentation.save_document import save_scraped_data_as_json
from codinit.documentation.pydantic_models import WebScrapingData, Metadata, Crawl

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
                languageCode="en"
            ),
            crawl=Crawl(
                loadedUrl="https://example.com",
                loadedTime="2021-01-01T00:00:00Z",
                referrerUrl="https://referrer.com",
                depth=1
            ),
            screenshotUrl="https://example.com/screenshot.png",
            html="<html></html>",
            markdown="## Example Markdown"
        )
    ]

def test_save_scraped_data_as_json(mocker, sample_data):
    # use mocker.patch to mock the built-in open function
    # allows to track how open is called without actually performing file operations.
    mock_file_open = mocker.patch('builtins.open', mocker.mock_open())

    filename = "test_data.json"
    save_scraped_data_as_json(sample_data, filename)

    # Construct the expected JSON string
    expected_json_str = json.dumps(
        [{"url": item.url, "text": item.text, "metadata": item.metadata.dict()} for item in sample_data],
        ensure_ascii=False,
        indent=4
    )

    # checks that the function save_scraped_data_as_json called the funciton open with the correct arguments
    # purpose: ensure that function interacts with the file system as expected
    mock_file_open.assert_called_once_with(filename, 'w', encoding='utf-8')

    # Concatenate all the arguments of write calls
    # because json.dump writes to the file object in multiple small chunks.
    written_content = "".join(call_args[0][0] for call_args in mock_file_open().write.call_args_list)

    # assert that the concatenated string matches the expected JSON content
    assert written_content == expected_json_str
