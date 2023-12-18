import pytest
from codinit.documentation.apify_webscraper import WebScraper  # Adjust the import path as needed
from apify_client import ApifyClient

mock_return_data = [
        {
        "url": "https://docs.apify.com/academy/web-scraping-for-beginners",
        "crawl": {
            "loadedUrl": "https://docs.apify.com/academy/web-scraping-for-beginners",
            "loadedTime": "2023-04-05T16:26:51.030Z",
            "referrerUrl": "https://docs.apify.com/academy",
            "depth": 0
        },
        "metadata": {
            "canonicalUrl": "https://docs.apify.com/academy/web-scraping-for-beginners",
            "title": "Web scraping for beginners | Apify Documentation",
            "description": "Learn how to develop web scrapers with this comprehensive and practical course. Go from beginner to expert, all in one place.",
            "author": None,
            "keywords": None,
            "languageCode": "en"
        },
        "screenshotUrl": None,
        "text": "Long text content...",
        "html": None,
        "markdown": "Markdown content..."
        },
    ]

def get_expected_run_input(url):
    return {
        'startUrls': [{'url': url}],
        # Include other default fields from the RunInput model
        'crawlerType': 'cheerio',
        'includeUrlGlobs': [],
        'excludeUrlGlobs': [],
        'ignoreCanonicalUrl': False,
        'maxCrawlDepth': 20,
        'maxCrawlPages': 9999999,
        'initialConcurrency': 0,
        'maxConcurrency': 200,
        'initialCookies': [],
        'proxyConfiguration': {'useApifyProxy': True},
        'requestTimeoutSecs': 60,
        'dynamicContentWaitSecs': 10,
        'maxScrollHeightPixels': 5000,
        'removeElementsCssSelector': 'nav, footer, script, style, noscript, svg,\n[role="alert"],\n[role="banner"],\n[role="dialog"],\n[role="alertdialog"],\n[role="region"][aria-label*="skip" i],\n[aria-modal="true"]',
        'removeCookieWarnings': True,
        'clickElementsCssSelector': '[aria-expanded="false"]',
        'htmlTransformer': 'readableText',
        'readableTextCharThreshold': 100,
        'aggressivePrune': False,
        'debugMode': False,
        'debugLog': False,
        'saveHtml': False,
        'saveMarkdown': True,
        'saveFiles': False,
        'saveScreenshots': False,
        'maxResults': 9999999
    }
@pytest.fixture
def mock_apify_client(mocker):
    mock_client = mocker.MagicMock(spec=ApifyClient)
    return mock_client

def test_run_scraping_basic(mock_apify_client):
    mock_apify_client.actor().call.return_value = {'defaultDatasetId': 'test_dataset_id'}
    mock_apify_client.dataset().iterate_items.return_value = mock_return_data

    actor_id = "test_actor_id"
    scraper = WebScraper(mock_apify_client, actor_id)

    test_urls = ["https://example.com"]
    results = scraper.run_scraping(test_urls)

    # Assertions to verify the results are returned
    assert results is not None
    assert len(results) > 0  # Ensure we have at least one result

    # Assuming we are testing with the provided sample data
    first_result = results[0]

    # Assertions for the first result
    assert first_result.url == "https://docs.apify.com/academy/web-scraping-for-beginners"
    assert first_result.crawl.loadedUrl == "https://docs.apify.com/academy/web-scraping-for-beginners"
    assert first_result.crawl.loadedTime == "2023-04-05T16:26:51.030Z"
    assert first_result.crawl.referrerUrl == "https://docs.apify.com/academy"
    assert first_result.crawl.depth == 0
    assert first_result.metadata.canonicalUrl == "https://docs.apify.com/academy/web-scraping-for-beginners"
    assert first_result.metadata.title == "Web scraping for beginners | Apify Documentation"
    assert first_result.metadata.description == "Learn how to develop web scrapers with this comprehensive and practical course. Go from beginner to expert, all in one place."
    assert first_result.metadata.languageCode == "en"
    assert first_result.text == "Long text content..."
    assert first_result.markdown == "Markdown content..."



def test_run_scraping_empty_dataset(mock_apify_client):
    mock_apify_client.actor().call.return_value = {'defaultDatasetId': 'test_dataset_id'}
    mock_apify_client.dataset().iterate_items.return_value = []

    actor_id = "test_actor_id"
    scraper = WebScraper(mock_apify_client, actor_id)

    test_urls = ["https://example.com"]
    results = scraper.run_scraping(test_urls)

    assert results == []  # Expecting an empty result for an empty dataset


def test_run_scraping_empty_url_list(mock_apify_client):
    mock_apify_client.actor().call.return_value = {'defaultDatasetId': 'test_dataset_id'}
    mock_apify_client.dataset().iterate_items.return_value = []

    actor_id = "test_actor_id"
    scraper = WebScraper(mock_apify_client, actor_id)

    test_urls = []
    results = scraper.run_scraping(test_urls)

    assert results == []  # Expecting an empty result for an empty URL list


def test_run_scraping_with_invalid_url_handled(mock_apify_client):
    mock_apify_client.actor().call.return_value = {'defaultDatasetId': 'test_dataset_id'}
    mock_apify_client.dataset().iterate_items.return_value = mock_return_data
    scraper = WebScraper(mock_apify_client, "test_actor_id")

    # Include an invalid URL in the test data
    test_urls = ["https://valid-url.com", "invalid-url"]

    results = scraper.run_scraping(test_urls)
    # Verify that the scraper processes the URL correctly
    # Check that 'actor' method of the client was called with the correct actor_id
    mock_apify_client.actor.assert_called_with("test_actor_id")

    # Construct the expected run_input, including all default fields
    # This will test that the actor got called only with the valif URL
    expected_run_input = get_expected_run_input("https://valid-url.com")

    # Check that 'call' method of the actor was called with the correct run_input
    mock_apify_client.actor().call.assert_called_once_with(run_input=expected_run_input)
    # Check if the valid URL is processed and the invalid one is skipped
    assert len(results) == 1  # Assuming only one valid URL


def test_run_scraping_with_valid_url(mock_apify_client):
    mock_apify_client.actor().call.return_value = {'defaultDatasetId': 'test_dataset_id'}
    mock_apify_client.dataset().iterate_items.return_value = mock_return_data

    scraper = WebScraper(mock_apify_client, "test_actor_id")

    test_url = "https://valid-url.com"
    scraper.run_scraping([test_url])

    # Verify that the scraper processes the URL correctly
    # Check that 'actor' method of the client was called with the correct actor_id
    mock_apify_client.actor.assert_called_with("test_actor_id")

    # Construct the expected run_input, including all default fields
    expected_run_input = get_expected_run_input(test_url)

    # Check that 'call' method of the actor was called with the correct run_input
    mock_apify_client.actor().call.assert_called_once_with(run_input=expected_run_input)

    # If you also want to check the results
    results = scraper.run_scraping([test_url])
    assert len(results) == 1  # Assuming one result for the valid URL
