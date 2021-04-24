import json
import os
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from queue import Queue

import requests
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning

from Crawler.AtomicCounter import AtomicCounter
from Parser.HTMLParser import MyHTMLParser

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class WebCrawler:
    root_url = "https://www.cs.uic.edu/"
    pages_to_crawl = 3000
    number_of_threads = 20
    threads_executor = ""
    visited_urls = None
    atomic_counter = AtomicCounter()
    file_contents_path = os.path.join(r'E:\IR\Project - Copy', r'url_contents')
    link_structures_path = os.path.join(r'E:\IR\Project - Copy', r'url_links')
    url_maps_path = r'./urlmaps.txt'
    base_url = "uic.edu"
    url_with_outgoing_links = dict()
    task_list = list()
    url_to_code = dict()

    def __init__(self):
        self.queue = Queue()
        self.threads_executor = ThreadPoolExecutor(max_workers=self.number_of_threads, thread_name_prefix="test")
        self.visited_urls = set()
        if not os.path.exists(self.file_contents_path):
            os.makedirs(self.file_contents_path)
        if not os.path.exists(self.link_structures_path):
            os.makedirs(self.link_structures_path)

    def start_crawling(self):
        try:
            self.queue.put(self.root_url)

            while self.atomic_counter.get_value() <= self.pages_to_crawl:
                #
                if self.atomic_counter.get_value() > self.pages_to_crawl:
                    self.threads_executor.shutdown(cancel_futures=True)
                    break
                if self.queue.empty():
                    # check if no thread has active job.
                    done, not_done = wait(self.task_list, return_when=ALL_COMPLETED)
                    print("Done task {} \n Not Done tasks {}".format(done, not_done))
                    if self.queue.empty():
                        break
                    # self.task_list.clear()
                    # if thread has a job, give continue keyword
                    # if thread does not have active job, break

                try:
                    url = self.queue.get()
                except Exception as e:
                    print("Exception", e)
                if url in self.visited_urls:
                    continue
                self.visited_urls.add(url)
                if self.atomic_counter.get_value() <= self.pages_to_crawl:
                    task = self.threads_executor.submit(self.process_url, url)
                    self.task_list.append(task)

            self.threads_executor.shutdown(cancel_futures=True)

            with open(self.url_maps_path, 'w') as file:
                file.write(json.dumps(self.url_with_outgoing_links))
            self.create_id_url_map()

        except Exception as e:
            print(e)

    def process_url(self, url):
        try:
            if self.atomic_counter.get_value() > self.pages_to_crawl:
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
            self.visited_urls.add(url)

    def get_links_from_url_content(self, json_object):
        result = json_object
        request_status = result["status"]
        if request_status == 200:
            links = self.parse_content(result["content"], result["url"])

            next_id = str(self.atomic_counter.increment())
            url_obj = {
                "url_id": next_id,
                "links": links
            }
            self.url_with_outgoing_links[result["url"]] = url_obj
            page_content = BeautifulSoup(result["content"], features="html.parser").get_text()

            self.write_content_to_persistent_storage(next_id, result["url"], page_content)
            for link in links:
                if link not in self.visited_urls:
                    self.queue.put(link)

    def write_content_to_persistent_storage(self, file_id, url_link, content):

        with open(os.path.join(self.file_contents_path, file_id), 'a+') as handle:
            file_object = {
                "url": url_link,
                "content": content
            }
            file_object_json = json.dumps(file_object)
            handle.write(file_object_json)

    def parse_content(self, content, url):

        html_parser = MyHTMLParser(url, self.base_url)
        html_parser.feed(content)
        links = html_parser.get_data()
        return links

    def create_id_url_map(self):
        urls = ""
        for root, dirs, files in os.walk(WebCrawler.file_contents_path):
            urls = files

        for url_file in urls:
            with open(os.path.join(WebCrawler.file_contents_path, url_file)) as handle:
                url = json.loads(handle.read())['url']
                url_id = url_file
                self.url_to_code[url] = url_id

        file_object_json = json.dumps(self.url_to_code)
        with open('url_code_map.json', "w+") as handle:
            handle.write(file_object_json)


c = WebCrawler()
c.start_crawling()
