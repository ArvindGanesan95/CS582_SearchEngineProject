import json
import os
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from queue import Queue

import requests
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning

from Crawler.AtomicCounter import AtomicCounter
from Parser.HTMLParser import MyHTMLParser

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class WebCrawler:
    root_url = "https://www.cs.uic.edu/"
    pages_to_crawl = 3000
    number_of_threads = 20
    threads_executor = ""
    visited_urls = None
    atomic_counter = AtomicCounter()
    file_contents_path = os.path.join(r'E:\IR\Project', r'url_contents')
    base_url = "uic.edu"
    url_with_outgoing_links = dict()
    task_list = list()

    def __init__(self):
        self.queue = Queue()
        self.threads_executor = ThreadPoolExecutor(max_workers=self.number_of_threads, thread_name_prefix="test")
        self.visited_urls = set()
        if not os.path.exists(self.file_contents_path):
            os.makedirs(self.file_contents_path)

    def start_crawling(self):
        try:
            self.queue.put(self.root_url)
            while self.atomic_counter.get_value() <= self.pages_to_crawl:
                #
                if self.atomic_counter.get_value() > self.pages_to_crawl:
                    self.threads_executor.shutdown(cancel_futures=True)
                    break

                # while self.queue.empty():
                #     pass

                if self.queue.empty():
                    # check if no thread has active job.
                    done, not_done = wait(self.task_list, return_when=ALL_COMPLETED)
                    if self.queue.empty():
                        break
                    # self.task_list.clear()
                    # if thread has a job, give continue keyword
                    # if thread does not have active job, break

                # print("hello")
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

                # task.add_done_callback(self.get_links_from_url_content)
                # self.write_content_to_persistent_storage(url)

            # print(self.url_with_outgoing_links)

            self.threads_executor.shutdown(cancel_futures=True)

            with open('urlmaps.txt', 'w') as file:
                file.write(json.dumps(self.url_with_outgoing_links))

        except Exception as e:
            print(e)

    def process_url(self, url):
        try:
            # print(threading.current_thread().name)
            if self.atomic_counter.get_value() > self.pages_to_crawl:
                return
            # try:
            #     url = self.queue.get()
            #     if url in self.visited_urls:
            #         return
            #     self.visited_urls.add(url)
            print(url)
            # except Exception as e:
            #     print(e)
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
        # print(result["url"])
        if request_status == 200:
            links = self.parse_content(result["content"], result["url"])

            # print(result["url"], result)
            # if result["url"] in self.url_with_outgoing_links:
            self.url_with_outgoing_links[result["url"]] = links
            # else:
            #     self.url_with_outgoing_links[result["url"]] = []
            #     self.url_with_outgoing_links[result["url"]].append(link)
            page_content = BeautifulSoup(result["content"], features="html.parser").get_text()
            # print("SIZE", len(self.url_with_outgoing_links.keys()))
            self.write_content_to_persistent_storage(result["url"], page_content)
            self.write_links_to_persistent_storage(result["url"], links)
            for link in links:
                if link not in self.visited_urls:
                    self.queue.put(link)

    def write_content_to_persistent_storage(self, url_link, content):
        next_id = str(self.atomic_counter.increment())
        with open(os.path.join(self.file_contents_path, next_id), 'a+') as handle:
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

    def write_links_to_persistent_storage(self, url, links):
        pass


c = WebCrawler()
c.start_crawling()
