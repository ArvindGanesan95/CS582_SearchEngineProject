import json
import urllib.parse
from abc import ABC
from html.parser import HTMLParser

exclusion_filter = ['.gif', '.jpeg', '.ps', '.pdf', '.ppt', '.xml', '.docx']
base_url = "uic.edu"
global_url = ""


def filterAnchorTags(links, web_url):
    result = set()
    global global_url
    global_url = web_url
    for link in links:
        if link.get('href') is not None:
            if link.get('href').startswith('#'):
                continue

            result.add(urllib.parse.urljoin(web_url, link.get('href').strip()))

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
        parts = urllib.parse.urlsplit(url)
        if parts.scheme == "http" or parts.scheme == "https":

            base = "{0.netloc}".format(parts)
            scheme = "{0.scheme}".format(parts)
            query = "{0.query}".format(parts)
            if scheme == "http":
                scheme = "https"
            new_base_url = "{}://{}".format(scheme, base)
            path = urllib.parse.urljoin(new_base_url, parts.path)
            # path = url[:url.rfind('/') + 1] if '/ ' in parts.path else url
            if path == "https://www.uic.edu/depts/oaa/diversity/":
                print("hi", url, global_url)
            refined_results.append(path)
    return refined_results

# class MyHTMLParser(HTMLParser, ABC):
#     links = None
#     base_url = None
#     root_url = None
#     exclusion_filter = ['.gif', '.jpeg', '.ps', '.pdf', '.ppt', '.xml', '.docx']
#
#     def reset(self):
#         super().reset()
#         self.links = list()
#
#     def __init__(self, root_url=None, base_url=None):
#         super().__init__()
#         self.base_url = base_url
#         self.root_url = root_url
#
#     def handle_starttag(self, tag, attrs):
#         if tag == 'a':
#             for (name, value) in attrs:
#                 if name == 'href':
#                     if self.is_valid_link(value) is True:
#                         is_extension_valid = True
#                         for extension in self.exclusion_filter:
#                             if value.endswith(extension):
#                                 is_extension_valid = False
#                                 break
#
#                         if not is_extension_valid:
#                             print("Skipping url {}".format(value))
#                             continue
#
#                         new_url = ""
#
#                         if value.startswith('/'):
#                             value = value[1:]
#                         if value.endswith('/'):
#                             value = value[:-1]
#
#                         value = urllib.parse.urljoin(self.root_url, value)
#                         url_object = urllib.parse.urlparse(value)
#                         new_url = url_object.netloc
#                         if url_object.netloc.startswith("www."):
#                             new_url = url_object.netloc.split("www.")[1]
#                         subdomain_path = url_object.path
#                         if url_object.path.startswith('/'):
#                             subdomain_path = url_object.path[1:]
#
#                         http_protocol = url_object.scheme
#                         if http_protocol == 'http':
#                             http_protocol = 'https'
#                         new_url = "{}://{}".format(http_protocol, new_url)
#
#                         new_url = urllib.parse.urljoin(new_url, subdomain_path)
#                         # else:
#                         #
#                         #     new_url = value
#                         # print("Input URL", self.root_url)
#                         if new_url.endswith('pdf'):
#                             print("hi", self.root_url, value)
#                             return
#                         # print("NEW URL ", new_url)
#                         self.links.append(new_url)
#
#     def is_valid_link(self, url):
#         is_valid = False
#
#         if url.startswith('#'):
#             is_valid = False
#
#         elif url.startswith('/'):
#             is_valid = True
#
#         else:
#             url_object = urllib.parse.urlparse(url)
#
#             if (url_object.scheme == 'http' or url_object.scheme == 'https') \
#                     and self.is_extension_valid(url_object.netloc, url_object.path, url):
#                 is_valid = True
#
#         return is_valid
#
#     def get_data(self):
#         return self.links
#
#     def is_extension_valid(self, domain, path, url):
#         if url == 'http://fimweb.fim.uic.edu/Images/Maps/Visitor%20East%20Side.pdf':
#             print("hi")
#         if self.base_url not in domain:
#             return False
#
#         for extension in self.exclusion_filter:
#             if path.endswith(extension):
#                 return False
#         return True
#
#
# if __name__ == '__main__':
#     p = MyHTMLParser("uic.edu", "uic.edu")
#     # u = urllib.parse.urljoin('http://www.uic.edu', 'http://cs.uic.edu/wp-content/uploads/sites/110/2021/04'
#     # '/Recommendation_for_Research_Assistantship_Fillable-PDF-v-4.9.21.pdf')
#
#     print(p.is_valid_link(
#         'https://dos.uic.edu/student-veterans-affairs/wp-content/uploads/sites/262/2021/03/P2100486_DOS_Student-Handbook-Spring-2021-2.pdf'))
# #     obj = dict()
# #     keys = list()
# #     with open(r'E:\IR\Project - Copy\Computations\urlmaps.txt') as h:
# #         obj = json.loads(h.read())
# #         keys = list(obj.keys())
# #     with open(r'E:\IR\Project - Copy\Computations\urlkeys.txt', "w+") as h:
# #         h.writelines("URL %s\n" % place for place in keys)
