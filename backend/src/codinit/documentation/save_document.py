import json
from typing import List

from pydantic import TypeAdapter

from codinit.documentation.pydantic_models import WebScrapingData


def save_scraped_data_as_json(data: List[WebScrapingData], filename: str):
    """
    saves data in json file, overwrites the file.
    TODO check if URL has been already visited and only save new data, or check for changes..
    Better to be done with some DB.
    """
    serialized_data = [item.model_dump() for item in data]
    with open(filename, "w", encoding="utf-8") as file:
        # create json file which contains list of WebScrapingData objects
        json.dump(serialized_data, file, ensure_ascii=False, indent=4)


def load_scraped_data_from_json(filename: str) -> List[WebScrapingData]:
    """
    loads WebScrapingData models from json file
    """
    with open(filename, "r", encoding="utf-8") as file:
        # load json file which contains list of WebScrapingData objects
        data = json.load(file)
        typeadapter = TypeAdapter(WebScrapingData)
        # create list of WebScrapingData models from json data
        return [typeadapter.validate_python(item) for item in data]


if __name__ == "__main__":
    from apify_client import ApifyClient

    from codinit.config import secrets
    from codinit.documentation.apify_webscraper import WebScraper

    client = ApifyClient(secrets.apify_key)
    scraper = WebScraper(client)
    scraped_data_models = scraper.scrape_urls(
        urls=["https://docs.apify.com/academy/web-scraping-for-beginners"]
    )
    for model in scraped_data_models:
        print(model.text)
    filename = "/apify_test.json"
    save_scraped_data_as_json(
        data=scraped_data_models, filename=secrets.docs_dir + filename
    )
    data = load_scraped_data_from_json(filename=secrets.docs_dir + filename)
    for model in data:
        print(model.text)
