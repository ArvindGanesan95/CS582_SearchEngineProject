"""
Submitted by,
Arvind Ganesan
NETID: aganes25@uic.edu
"""
import urllib.parse

# Set of exclusion filter to be checked for every url


exclusion_filter = [".gif", ".jpeg", ".ps", ".pdf", ".ppt", ".xml", ".docx"]
global_url = ""
base_url = "uic.edu"


# Function check the href attribute of anchor tag
def filterAnchorTags(links, web_url):
    result = set()
    global global_url
    global_url = web_url
    if web_url is None:
        return result
    for link in links:
        if link.get("href") is not None:
            if link.get("href").startswith("#"):
                continue

            result.add(urllib.parse.urljoin(web_url, link.get("href").strip()))

    return result


# Function to check if the url falls into any of exclusion filter
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


# Function to check if the url satisfies the domain given in the crawler
def filterDomainUrls(urls):
    refined_results = []
    for url in urls:
        if base_url in url:
            refined_results.append(url)
    return refined_results


# Function to allow only http or https protocols, change http to https protocol, form the new url
# The protocol is changed to https to avoid duplicates
def formCorrectUrls(urls):
    refined_results = []
    for url in urls:
        # extract base url to resolve relative links
        parts = urllib.parse.urlsplit(url)
        if parts.scheme == "http" or parts.scheme == "https":

            base = "{0.netloc}".format(parts)
            scheme = "{0.scheme}".format(parts)
            if scheme == "http":
                scheme = "https"
            new_base_url = "{}://{}".format(scheme, base)
            path = urllib.parse.urljoin(new_base_url, parts.path)
            refined_results.append(path)
    return refined_results
