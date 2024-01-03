import datetime
from typing import List

from apify_client import ApifyClient
from pydantic import HttpUrl, TypeAdapter, ValidationError

from codinit.documentation.pydantic_models import RunInput, StartUrl, WebScrapingData


class WebScraper:
    def __init__(self, client: ApifyClient, actor_id: str = "aYG0l9s7dbB7j3gbS"):
        self.client = client
        self.actor_id = actor_id

    def run_scraping(self, urls: List[HttpUrl]) -> List[WebScrapingData]:
        # contruct start urls models from url list
        startUrls = []
        for url in urls:
            try:
                startUrls.append(StartUrl(url=url))
            except ValidationError as e:
                print(f"Invalid URL skipped: {url}. Reason: {e}")
                continue
        # construct crawling input object
        run_input = RunInput(
            startUrls=startUrls
            # Other fields will use default values unless specified
        )
        start = datetime.datetime.now()
        # call website content crawler from apify, which has id aYG0l9s7dbB7j3gbS
        run = self.client.actor(self.actor_id).call(run_input=run_input.model_dump())

        # Initialize an empty list to store Pydantic models
        scraped_data_models: List[WebScrapingData] = []

        # Fetch and parse Actor results from the run's dataset (if there are any)
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            # handle potential validation errors when parsing items
            try:
                adapter = TypeAdapter(WebScrapingData)
                model = adapter.validate_python(item)
                scraped_data_models.append(model)
            except ValidationError as e:
                print("Error parsing item to model:", e)
        end = datetime.datetime.now()
        # Print the duration of the scraping process
        print(f"scraping duration={end-start}")
        return scraped_data_models

    def scrape_urls(self, urls: List[str]) -> List[WebScrapingData]:
        # parse urls to HttpUrls
        # TODO in pydantic v2 use TypeAdapter
        # https://stackoverflow.com/questions/72567679/why-i-cannot-create-standalone-object-of-httpurl-in-pydantic
        ta = TypeAdapter(HttpUrl)
        parsed_urls: List[HttpUrl] = [ta.validate_python(url) for url in urls]
        return self.run_scraping(urls=parsed_urls)  # type: ignore


if __name__ == "__main__":
    from codinit.config import secrets

    client = ApifyClient(secrets.apify_key)
    scraper = WebScraper(client)
    scraped_data_models = scraper.scrape_urls(
        urls=["https://docs.apify.com/academy/web-scraping-for-beginners"]
    )
    for model in scraped_data_models:
        print(model.text)
