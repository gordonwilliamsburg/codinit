import os
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


def download_html_only(start_url: str, folder: str) -> None:
    """
    Download all .html files from a given URL.

    This function sends a GET request to the given URL, and writes the response text
    to a new file in the specified folder. It then looks for all hyperlinks in the
    HTML, and if the hyperlink ends with '.html', it adds the linked HTML URL
    to a queue for processing.

    Parameters:
    start_url (str): The URL to download HTML files from.
    folder (str, optional): The folder where downloaded files will be saved. Defaults to the current directory.
    """
    # Initialize an empty set for processed URLs and a queue for URLs to be processed
    processed_urls = set()
    queue = [start_url]

    while queue:
        url = queue.pop(0)

        if url not in processed_urls:
            processed_urls.add(url)

            # Send a GET request to the URL
            response = requests.get(url)

            # Construct the filename using the last part of the URL
            filename = url.split("/")[-1] or (urlparse(url).netloc + ".html")
            filename = os.path.join(folder, filename)
            print(filename)
            print("-------------")
            # Write the response text into a file
            with open(filename, "w") as file:
                file.write(response.text)

            # Parse the response text with BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")

            # For all 'a' tags (hyperlinks) in the HTML, if the href ends with '.html', add to queue
            for link in soup.find_all("a"):
                href = link.get("href")
                if href and href.endswith(".html"):
                    full_url = urljoin(url, href)
                    if full_url not in processed_urls:
                        queue.append(full_url)


def download_html(start_url: str, folder: str = ".") -> None:
    """
    Download all web pages from a given URL within the same domain.

    This function sends a GET request to the given URL, and writes the response text
    to a new file in the specified folder. It then looks for all hyperlinks in the
    HTML, and if the hyperlink is within the same domain, it adds the linked URL
    to a queue for processing.

    Parameters:
    start_url (str): The URL to download web pages from.
    folder (str, optional): The folder where downloaded files will be saved. Defaults to the current directory.
    """
    # Parse the start URL to get the domain
    start_domain = urlparse(start_url).netloc

    # Initialize an empty set for processed URLs and a queue for URLs to be processed
    processed_urls = set()
    queue = [start_url]

    while queue:
        url = queue.pop(0)

        if url not in processed_urls:
            processed_urls.add(url)

            # Send a GET request to the URL
            response = requests.get(url)

            # Construct the filename using the URL path, replacing slashes with underscores
            filename = (
                url.replace("https://", "").replace("http://", "").replace("/", "_")
            )
            filename = os.path.join(folder, filename + ".html")
            # Write the response text into a file
            with open(filename, "w") as file:
                file.write(response.text)

            print(f"downloaded {url}")
            print("-------------")
            # Parse the response text with BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")

            # For all 'a' tags (hyperlinks) in the HTML, if the href is within the same domain, add to queue
            for link in soup.find_all("a"):
                href = link.get("href")
                if href:
                    full_url = urljoin(url, href)
                    # Check if the linked URL is within the same domain
                    if (
                        urlparse(full_url).netloc == start_domain
                        and full_url not in processed_urls
                    ):
                        queue.append(full_url)
