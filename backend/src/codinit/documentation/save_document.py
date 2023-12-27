import json
from typing import List

from pydantic import HttpUrl, parse_obj_as

from codinit.documentation.pydantic_models import WebScrapingData


def save_scraped_data_as_json(data: List[WebScrapingData], filename: str):
    """
    saves data in json file, overwrites the file.
    TODO check if URL has been already visited and only save new data, or check for changes..
    Better to be done with some DB.
    """
    with open(filename, "w", encoding="utf-8") as file:
        json_data = [
            {"url": item.url, "text": item.text, "metadata": item.metadata.dict()}
            for item in data
        ]
        json.dump(json_data, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    from apify_client import ApifyClient

    from codinit.config import secrets
    from codinit.documentation.apify_webscraper import WebScraper

    client = ApifyClient(secrets.apify_key)
    scraper = WebScraper(client)
    # TODO in pydantic v2 use TypeAdapter
    # https://stackoverflow.com/questions/72567679/why-i-cannot-create-standalone-object-of-httpurl-in-pydantic
    url = parse_obj_as(
        HttpUrl, "https://docs.apify.com/academy/web-scraping-for-beginners"
    )
    urls = [url]
    scraped_data_models = scraper.run_scraping(urls=urls)
    for model in scraped_data_models:
        print(model.text)
    filename = "/apify_test.json"
    save_scraped_data_as_json(scraped_data_models, secrets.docs_dir + filename)
