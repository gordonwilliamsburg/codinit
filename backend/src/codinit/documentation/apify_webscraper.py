import datetime
from typing import List

from apify_client import ApifyClient
from pydantic import HttpUrl, ValidationError, parse_obj_as

from codinit.documentation.pydantic_models import RunInput, StartUrl, WebScrapingData


class WebScraper:
    def __init__(self, client: ApifyClient, actor_id: str = "aYG0l9s7dbB7j3gbS"):
        self.client = client
        self.actor_id = actor_id

    def run_scraping(self, urls: List[HttpUrl]) -> List[WebScrapingData]:
        # contruct start urls models from url list
        startUrls = [StartUrl(url=url) for url in urls]
        # construct crawling input object
        run_input = RunInput(
            startUrls=startUrls
            # Other fields will use default values unless specified
        )
        start = datetime.datetime.now()
        # call website content crawler from apify, which has id aYG0l9s7dbB7j3gbS
        run = self.client.actor(self.actor_id).call(run_input=run_input.dict())

        # Initialize an empty list to store Pydantic models
        scraped_data_models: List[WebScrapingData] = []

        # Fetch and parse Actor results from the run's dataset (if there are any)
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            # handle potential validation errors when parsing items
            try:
                model = parse_obj_as(WebScrapingData, item)
                scraped_data_models.append(model)
            except ValidationError as e:
                print("Error parsing item to model:", e)
        end = datetime.datetime.now()
        # Print the duration of the scraping process
        print(f"scraping duration={end-start}")
        return scraped_data_models


if __name__ == "__main__":
    from codinit.config import secrets

    client = ApifyClient(secrets.apify_key)
    scraper = WebScraper(client)
    urls = [HttpUrl(url="https://docs.apify.com/academy/web-scraping-for-beginners")]
    scraped_data_models = scraper.run_scraping(urls=urls)
    for model in scraped_data_models:
        print(model.text)
