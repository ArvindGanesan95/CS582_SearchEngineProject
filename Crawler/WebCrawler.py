"""
Submitted by,
Arvind Ganesan
NETID: aganes25@uic.edu
"""

import json
import os
import shutil
from abc import abstractmethod, ABC
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from queue import Queue
import fastcounter
import requests
from bs4 import BeautifulSoup
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from Parser.HTMLParser import (
    filterAnchorTags,
    filterExclusionUrls,
    filterDomainUrls,
    formCorrectUrls,
)
from Utilities.Globals import (
    file_contents_path,
    computations_path,
    code_to_url_map_path,
    url_to_code_map_path,
    url_maps_path,
)

# Suppress only the single warning from urllib3 needed.
disable_warnings(InsecureRequestWarning)


# Write a decorator function to handle exceptions. This makes adding try/catch clauses
# to be written in one place instead of adding them to each and every required position
def exception_handler(func):
    def exception_function(*args, **kwargs):
        try:
            value = func(*args, **kwargs)
            return value
        except Exception as e:
            print(f"Exception in {func.__name__} :: ", e)
            raise e

    return exception_function


# An abstract class to denote a generic crawler
class WebCrawler(ABC):
    root_url = "https://www.cs.uic.edu/"
    base_url = "uic.edu"
    pages_to_crawl = 3000
    url_with_outgoing_links = dict()

    @abstractmethod
    def crawl(self):
        pass


# An inherited crawler class that uses ThreadPool and applies BFS strategy to perform crawling
class SpiderCrawler(WebCrawler):
    number_of_threads = 1
    threads_executor = None
    visited_urls = None
    unique_counter = fastcounter.Counter()
    task_list = list()

    def __init__(
            self, root_url=None, base_url=None, pages_to_crawl=None, number_of_workers=10
    ):
        shutil.rmtree(file_contents_path, ignore_errors=True)
        shutil.rmtree(computations_path, ignore_errors=True)
        if not os.path.exists(file_contents_path):
            os.makedirs(file_contents_path)
        if not os.path.exists(computations_path):
            os.makedirs(computations_path)
        self.code_to_url = dict()
        self.url_to_code = dict()
        self.queue = Queue()
        if pages_to_crawl is not None:
            self.pages_to_crawl = pages_to_crawl
        if base_url is not None:
            self.base_url = base_url
        if root_url is not None:
            self.root_url = root_url
        if number_of_workers > 20:
            self.number_of_threads = 20
        elif number_of_workers > 0:
            self.number_of_threads = number_of_workers
        self.threads_executor = ThreadPoolExecutor(
            max_workers=self.number_of_threads, thread_name_prefix="worker"
        )
        self.visited_urls = set()

    def crawl(self):
        try:
            print(
                "Crawling {} with {} number of workers".format(
                    self.root_url, self.number_of_threads
                )
            )
            # Add root url to the queue to perform BFS to crawl pages
            self.queue.put(self.root_url)
            # Run always until the threshold pages are crawled or queue is empty
            while True:
                # If threshold pages are crawled, cancel pending thread tasks and exit
                if self.unique_counter.value >= self.pages_to_crawl:
                    self.threads_executor.shutdown(cancel_futures=True)
                    break
                # If queue is empty, wait for all threads to finish their work
                if self.queue.empty():
                    wait(self.task_list, return_when=ALL_COMPLETED)
                    # if the queue is still empty, there are no more pages to crawl
                    if self.queue.empty():
                        break
                url = ""
                try:
                    url = self.queue.get()
                except Exception as e:
                    print(e)
                # If the url is already visited, move on to next url
                if url in self.visited_urls:
                    continue
                # Mark url as visited
                self.visited_urls.add(url)
                # If the threshold pages are not yet reached, submit the url to a thread for further processing
                if self.unique_counter.value <= self.pages_to_crawl:
                    task = self.threads_executor.submit(self.process_url, url)
                    self.task_list.append(task)

            print(self.url_with_outgoing_links)
            # Write the link structure of collection (url->outgoing_links) to file system for later processing
            with open(url_maps_path, "w") as file:
                file.write(json.dumps(self.url_with_outgoing_links))
            # Create a map of (url->uniqueID) and (uniqueID->url) to be used for ranking algorithms
            self.create_id_url_map()

        except Exception as e:
            print(e)
            raise e

    # Function that is executed by a thread. The function makes a network request to the url to get its content.
    # The content is then analyzed for fetching the outgoing links.
    def process_url(self, url):
        try:
            # Check if threshold pages are reached. Due to multithreading, it is possible for an other thread
            # to process a url asynchronously. Checking everytime before processing would minimally guarantee
            # that the page processed will be a worthy computation
            if self.unique_counter.value >= self.pages_to_crawl:
                return
            print(url)
            value = {}
            with requests.get(url, verify=False, timeout=120) as conn:
                # Create Dictionary
                value = {
                    "status": conn.status_code,
                    "content": conn.text,
                    "url": url,
                }
            self.get_links_from_url_content(value)

        except Exception as e:
            print(str(e))
            raise e

    # Function to add unvisited outgoing links from the html page content of a url. The anchor tags with href attribute
    # are searched and filtered
    @exception_handler
    def get_links_from_url_content(self, json_object):
        result = json_object
        request_status = result["status"]
        if request_status == 200:

            page_object = BeautifulSoup(result["content"], features="html.parser")
            links = self.parse_content(page_object, result["url"])
            # Append the outgoing links to the global map to update link structure
            self.url_with_outgoing_links[result["url"]] = links
            self.write_content_to_persistent_storage(result["url"], result["content"])
            for link in links:
                # Check if url is not visited already. it is possible that the same outgoing link
                # may be visited by different threads from different parent urls
                if link not in self.visited_urls:
                    self.queue.put(link)

    # Function to write the url and its page text content to the file system
    @exception_handler
    def write_content_to_persistent_storage(self, url_link, content):
        # Get a unique id that acts a document id for the url before writing to file system.
        self.unique_counter.increment()
        next_id = str(self.unique_counter.value)
        with open(os.path.join(file_contents_path, next_id), "a+") as handle:
            file_object = {"url": url_link, "content": content}
            file_object_json = json.dumps(file_object)
            handle.write(file_object_json)

    # Function to fetch each of outgoing link from anchor tag of url. Each of the link is restricted to stay
    # within {base_url} domain and not match any of the extension given in exclusion filters
    @exception_handler
    def parse_content(self, soup, url):
        links = soup.find_all("a")
        result = filterAnchorTags(links, url)
        refined_results = filterExclusionUrls(result)
        refined_results_2 = filterDomainUrls(refined_results)
        result = formCorrectUrls(refined_results_2)
        return result

    # Function to create two maps (url->id and id->url) and write to file system
    def create_id_url_map(self):
        try:
            print("Inside create id url map function")
            urls = None
            for root, dirs, files in os.walk(file_contents_path):
                urls = files

            if urls is None:
                return

            for url_file in urls:
                with open(os.path.join(file_contents_path, url_file)) as handle:
                    url = json.loads(handle.read())["url"]
                    url_id = url_file
                    self.url_to_code[url] = url_id
                    self.code_to_url[url_id] = url

            with open(url_to_code_map_path, "w") as handle:
                handle.write(json.dumps(self.url_to_code))

            with open(code_to_url_map_path, "w") as handle:
                handle.write(json.dumps(self.code_to_url))

        except Exception as e:
            print("Exception occurred line 235", e)
            raise e
