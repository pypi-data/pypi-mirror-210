#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup as BS
import html2text as h2t
import hashlib
from .options import get_opts


def mkdir(asOutput: str):
    # TODO make output dir as needed
    pass


def writeUrl(
    asUrl: str,
    asOutput: str,
    abCode: bool,
    asTitle: str = "",
):
    h = h2t.HTML2Text()
    h.mark_code = abCode
    m = hashlib.md5()
    if asTitle != "":
        m.update(asTitle.encode("utf-8"))
    else:
        m.update(asUrl.encode("utf-8"))
    hashedUrl = m.hexdigest()
    response = requests.get(asUrl)
    with open(f"{asOutput}/{hashedUrl}.md", "w") as data:
        data.write(h.handle(response.text))
    pass


def writeUrls(asUrls: list, asOutput: str, abCode: bool):
    for url in asUrls:
        sUrl = url["href"]
        writeUrl(sUrl, asOutput, abCode, url.text)


def getUrls(
    asBaseUrl: str,
    abMatch: bool,
    asMatch: str,
) -> list:
    response = requests.get(asBaseUrl)
    soup = BS(response.text, "html.parser")
    urls = []
    for url in soup.findAll("a"):
        if abMatch:
            try:
                if asMatch in url["href"]:
                    urls.append(url)
            except KeyError:
                continue
        else:
            urls.append(url)
    return urls


def main():
    args = get_opts()
    # set vars
    bScrapeAll = args.all
    sBaseUrl = args.url
    bMatch = False if args.match is None else True
    sMatch = args.match
    sOutput = "." if args.output is None else args.output
    bCode = args.code
    # do da work
    if bScrapeAll:
        urls = getUrls(sBaseUrl, bMatch, sMatch)
        writeUrls(urls, sOutput, bCode)
    else:
        writeUrl(sBaseUrl, sOutput, bCode)
    return 0


if __name__ == "__main__":
    exit(main())
