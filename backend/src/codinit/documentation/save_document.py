import json
import logging
import os
from typing import List

from apify_client import ApifyClient
from pydantic import TypeAdapter

from codinit.config import Secrets, secrets
from codinit.documentation.apify_webscraper import WebScraper
from codinit.documentation.pydantic_models import WebScrapingData

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


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


class ScraperSaver:
    def __init__(
        self, libname: str, apify_client: ApifyClient, secrets: Secrets = secrets
    ):
        self.scraper = WebScraper(apify_client)
        self.secrets = secrets
        self.libname = libname
        self.filename = self.secrets.docs_dir + "/" + libname + ".json"

    def check_lib_docs_saved(self):
        if os.path.exists(self.filename):
            return True
        else:
            return False

    def scrape_and_save_apify_docs(self, urls: List[str]):
        if not self.check_lib_docs_saved():
            logging.info(
                "No library docs found for "
                + self.libname
                + " under "
                + self.filename
                + " , scraping..."
            )
            scraped_data_models = self.scraper.scrape_urls(urls=urls)
            save_scraped_data_as_json(data=scraped_data_models, filename=self.filename)
            logging.info(
                "Library docs saved " + self.libname + " under " + self.filename
            )
        else:
            logging.info("Library docs already exist " + self.libname)


if __name__ == "__main__":
    client = ApifyClient(secrets.apify_key)
    scraper_saver = ScraperSaver(libname="test", apify_client=client)
    urls = ["https://docs.apify.com/academy/web-scraping-for-beginners"]
    scraper_saver.scrape_and_save_apify_docs(urls=urls)
