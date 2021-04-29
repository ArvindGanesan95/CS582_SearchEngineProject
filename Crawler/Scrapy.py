from bs4 import BeautifulSoup as bs
import urllib.request
from urllib.parse import urljoin, urlsplit

from Parser.HTMLParser import exclusion_filter

base_url = "uic.edu"


def filterAnchorTags(links):
    result = set()
    for link in links:
        if link.get('href') is not None:
            if link.get('href').startswith('#'):
                continue

            result.add(urljoin(web_url, link.get('href').strip()))

    return result


def filterExclusionUrls(urls):
    refined_results = []
    for link in urls:
        is_valid = True
        for exclusion in exclusion_filter:
            if link.endswith(exclusion):
                is_valid = False
                break
        if is_valid:
            refined_results.append(link)
    return refined_results


def filterDomainUrls(urls):
    refined_results = []
    for url in urls:
        if base_url in url:
            refined_results.append(url)
    return refined_results


def formCorrectUrls(urls):
    refined_results = []
    for url in urls:
        # extract base url to resolve relative links
        parts = urlsplit(url)
        if parts.scheme == "http" or parts.scheme == "https":

            base = "{0.netloc}".format(parts)
            scheme = "{0.scheme}".format(parts)
            query = "{0.query}".format(parts)
            if scheme == "http":
                scheme = "https"
            base_url = "{}://{}".format(scheme, base)
            path = urljoin(base_url, parts.path)
            # path = url[:url.rfind('/') + 1] if '/ ' in parts.path else url
            refined_results.append(path)
    return refined_results


if __name__ == '__main__':
    web_url = 'https://www.uic.edu'
    sauce = urllib.request.urlopen(web_url).read()
    soup = bs(sauce, 'lxml')
    links = soup.find_all('a')
    result = filterAnchorTags(links)
    refined_results = filterExclusionUrls(result)

    refined_results_2 = filterDomainUrls(refined_results)

    newUrls = formCorrectUrls(refined_results_2)

    for link in newUrls:
        print(link)
