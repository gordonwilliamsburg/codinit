import json
from typing import List

from codinit.documentation.pydantic_models import WebScrapingData


def save_scraped_data_as_json(data: List[WebScrapingData], filename: str):
    """
    saves data in json file, overwrites the file.
    TODO check if URL has been already visited and only save new data, or check for changes..
    Better to be done with some DB.
    """
    with open(filename, "w", encoding="utf-8") as file:
        # create json file which contains list of WebScrapingData objects
        json.dump([item.dict() for item in data], file, ensure_ascii=False, indent=4)


def load_scraped_data_from_json(filename: str) -> List[WebScrapingData]:
    """
    loads WebScrapingData models from json file
    """
    with open(filename, "r", encoding="utf-8") as file:
        # load json file which contains list of WebScrapingData objects
        data = json.load(file)
        # create list of WebScrapingData models from json data
        return [WebScrapingData.parse_obj(item) for item in data]


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
