import itertools
import os
from abc import ABC
from html.parser import HTMLParser
import urllib.parse


class MyHTMLParser(HTMLParser, ABC):
    links = None
    base_url = None
    root_url = None
    exclusion_filter = ['.gif', '.jpeg', '.ps', '.pdf', '.ppt', '.xml']

    def reset(self):
        super().reset()
        self.links = list()

    def __init__(self, root_url=None, base_url=None):
        super().__init__()
        self.base_url = base_url
        self.root_url = root_url

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (name, value) in attrs:
                if name == 'href':
                    if self.is_valid_link(value):
                        new_url = ""

                        if value.startswith('/'):
                            if value.startswith('/'):
                                value = value[1:]
                            if value.endswith('/'):
                                value = value[:-1]

                            value = urllib.parse.urljoin(self.root_url, value)
                            url_object = urllib.parse.urlparse(value)

                            if url_object.netloc.startswith("www."):
                                new_url = url_object.netloc.split("www.")[1]
                            subdomain_path = ""
                            if url_object.path.startswith('/'):
                                subdomain_path = url_object.path[1:]

                            new_url = "{}://{}".format(url_object.scheme, url_object.netloc)

                            new_url = urllib.parse.urljoin(new_url, subdomain_path)
                        else:

                            new_url = value

                        self.links.append(new_url)

    def is_valid_link(self, url):
        is_valid = False

        if url.startswith('#'):
            is_valid = False

        elif url.startswith('/'):
            is_valid = True

        else:
            url_object = urllib.parse.urlparse(url)

            if url_object.scheme == 'http' or url_object.scheme == 'https' and \
                    self.base_url in url_object.netloc and self.is_extension_valid(url_object.netloc):
                is_valid = True

        return is_valid

    def get_data(self):
        return self.links

    def is_extension_valid(self, domain):
        if domain not in self.exclusion_filter:
            return True
        return False


p = MyHTMLParser("https://www.cs.uic.edu/", "uic.edu")
p.feed("")