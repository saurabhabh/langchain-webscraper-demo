import argparse
from logging import log
from warnings import catch_warnings
import requests
import os
from urllib.parse import urlparse
from collections import defaultdict
from bs4 import BeautifulSoup
import json

parser = argparse.ArgumentParser()
parser.add_argument("--site", type=str, required=True)
parser.add_argument("--depth", type=int, default=3)


def cleanUrl(url: str):
    return url.replace("https://", "").replace("/", "-").replace(".", "_")


def get_response_and_save(url: str):
    try:
        response = requests.get(url)
        log(1,response.json)
        if not os.path.exists("./scrape"):
            os.mkdir("./scrape")
        parsedUrl = cleanUrl(url)
        with open("./scrape/" + parsedUrl + ".html", "wb") as f:
            f.write(response.content)
        return response
    except:
        print("An exception occurred")
        the_response =  requests.Response()
        the_response.code = "expired"
        the_response.error_type = "expired"
        the_response.status_code = 400
        the_response._content = b'{ "key" : "a" }'
        return the_response

def scrape_links(
    scheme: str,
    origin: str,
    path: str,
    depth=3,
    sitemap: dict = defaultdict(lambda: ""),
):
    siteUrl = scheme + "://" + origin + path
    cleanedUrl = cleanUrl(siteUrl)

    if depth < 0:
        return
    if sitemap[cleanedUrl] != "":
        return

    sitemap[cleanedUrl] = siteUrl
    response = get_response_and_save(siteUrl)
    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.find_all("a")

    for link in links:
        href = urlparse(link.get("href"))
        if (href.netloc != origin and href.netloc != "") or (
            href.scheme != "" and href.scheme != "https"
        ):
            continue
        scrape_links(
            href.scheme or "https",
            href.netloc or origin,
            href.path,
            depth=depth - 1,
            sitemap=sitemap,
        )
    return sitemap


if __name__ == "__main__":
    args = parser.parse_args()
    url = urlparse(args.site)
    sitemap = scrape_links(url.scheme, url.netloc, url.path, depth=args.depth)
    with open("./scrape/sitemap.json", "w") as f:
        f.write(json.dumps(sitemap))
