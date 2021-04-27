# import json
# import os
# import shutil
# import urllib.parse
# from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
# from queue import Queue
#
# import requests
# from bs4 import BeautifulSoup
# from urllib3.exceptions import InsecureRequestWarning
#
# from Crawler.AtomicCounter import AtomicCounter
# from Parser.HTMLParser import MyHTMLParser
#
# requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
#
#
# def make_request(url):
#     pass
#
#
# class WebCrawler:
#     root_url = "https://cs.uic.edu/"
#     pages_to_crawl = 3200
#     number_of_threads = 22
#     threads_executor = ""
#     visited_urls = None
#     atomic_counter = AtomicCounter()
#     computations_path = os.path.join(r'E:\IR\Project - Copy', 'Computations')
#     file_contents_path = os.path.join(r'E:\IR\Project - Copy', r'url_contents')
#     link_structures_path = os.path.join(r'E:\IR\Project - Copy', r'url_links')
#     url_to_code_map_path = os.path.join(r'E:\IR\Project - Copy', 'Computations', 'url_code_map.json')
#     code_to_url_map_path = os.path.join(r'E:\IR\Project - Copy', 'Computations', 'code_to_url_map.json')
#     url_maps_path = os.path.join(r'E:\IR\Project - Copy', 'Computations', r'urlmaps.txt')
#     base_url = "uic.edu"
#     url_with_outgoing_links = dict()
#     task_list = list()
#     url_to_code = dict()
#     code_to_url = dict()
#
#     def __init__(self):
#         self.queue = Queue()
#         self.threads_executor = ThreadPoolExecutor(max_workers=self.number_of_threads, thread_name_prefix="worker")
#         self.visited_urls = set()
#         shutil.rmtree(self.file_contents_path)
#         shutil.rmtree(self.computations_path)
#         if not os.path.exists(self.file_contents_path):
#             os.makedirs(self.file_contents_path)
#         if not os.path.exists(self.computations_path):
#             os.makedirs(self.computations_path)
#
#     def start_crawling(self):
#         try:
#             with requests.get(self.root_url, verify=False, timeout=120) as conn:
#                 self.root_url = conn.url
#
#             self.queue.put(self.root_url)
#
#             while True:
#                 #
#                 if self.atomic_counter.get_value() >= self.pages_to_crawl:
#                     self.threads_executor.shutdown(cancel_futures=True)
#                     break
#
#                 if self.queue.empty():
#                     # check if no thread has active job.
#                     done, not_done = wait(self.task_list, return_when=ALL_COMPLETED)
#                     if self.queue.empty():
#                         break
#                     # self.task_list.clear()
#                     # if thread has a job, give continue keyword
#                     # if thread does not have active job, break
#
#                 # print("hello")
#                 try:
#                     url = self.queue.get()
#                 except Exception as e:
#                     print(e)
#                 if url in self.visited_urls:
#                     continue
#                 self.visited_urls.add(url)
#                 if len(self.task_list) <= self.pages_to_crawl:
#                     task = self.threads_executor.submit(self.process_url, url)
#                     self.task_list.append(task)
#             # Cancel all active threads since the threshold pages have reached. This function does not
#             # guarantee immediate stopping of all threads at the same time. s
#             self.threads_executor.shutdown(cancel_futures=True)
#
#             # Write the map of node:outgoing links to file system
#             with open(self.url_maps_path, 'w') as file:
#                 file.write(json.dumps(self.url_with_outgoing_links))
#             # Create a map of unique id for every url
#             self.create_id_url_map()
#
#         except Exception as e:
#             print("103", e)
#
#     # Function to make a request to url to get its page contents
#     def process_url(self, url):
#         try:
#             #
#
#             # Exit early if the threshold pages are already processed
#             if self.atomic_counter.get_value() > self.pages_to_crawl:
#                 return
#
#             value = {}
#             temp = url
#             # self.visited_urls.add(url)
#             with requests.get(url, verify=False, timeout=120) as conn:
#                 # Create Dictionary
#                 value = {
#                     "status": conn.status_code,
#                     "content": conn.text,
#                     "url": conn.url,
#                 }
#                 url = conn.url
#             self.visited_urls.add(url)
#             self.get_links_from_url_content(value)
#
#             # print("Scraped URL ", url)
#
#         except Exception as e:
#             print("131 Exception occurred", str(e))
#             self.visited_urls.add(url)
#
#     def get_links_from_url_content(self, json_object):
#         result = json_object
#         request_status = result["status"]
#         # print(result["url"])
#         if request_status == 200:
#             links = self.parse_content(result["content"], result["url"])
#
#             # print(result["url"], result)
#             # if result["url"] in self.url_with_outgoing_links:
#             self.url_with_outgoing_links[result["url"]] = links
#             # else:
#             #     self.url_with_outgoing_links[result["url"]] = []
#             #     self.url_with_outgoing_links[result["url"]].append(link)
#             page_content = BeautifulSoup(result["content"], features="html.parser").get_text()
#             # print("SIZE", len(self.url_with_outgoing_links.keys()))
#             self.write_content_to_persistent_storage(result["url"], page_content)
#             #self.write_links_to_persistent_storage(result["url"], links)
#             for link in links:
#                 if link not in self.visited_urls:
#                     self.queue.put(link)
#
#     # def get_links_from_url_content(self, json_object):
#     #     result = json_object
#     #     request_status = result["status"]
#     #     if request_status == 200:
#     #         links = self.parse_content(result["content"], result["url"])
#     #
#     #         next_id = str(self.atomic_counter.increment())
#     #         url_obj = {
#     #             "url_id": next_id,
#     #             "links": links
#     #         }
#     #         self.url_with_outgoing_links[result["url"]] = url_obj
#     #         page_content = BeautifulSoup(result["content"], features="html.parser").get_text()
#     #
#     #         self.write_content_to_persistent_storage(next_id, result["url"], page_content)
#     #         for link in links:
#     #             if link not in self.visited_urls:
#     #                 # resolved_url = make_request(url)
#     #                 self.queue.put(link)
#
#     # Function to write the url and its content to file system
#     def write_content_to_persistent_storage(self, url_link, content):
#         next_id = str(self.atomic_counter.increment())
#         with open(os.path.join(self.file_contents_path, next_id), 'a+') as handle:
#             file_object = {
#                 "url": url_link,
#                 "content": content
#             }
#             file_object_json = json.dumps(file_object)
#             handle.write(file_object_json)
#
#     # def write_content_to_persistent_storage(self, file_id, url_link, content):
#     #
#     #     try:
#     #
#     #         with open(os.path.join(self.file_contents_path, file_id), 'a+') as handle:
#     #             file_object = {
#     #                 "url": url_link,
#     #                 "content": content
#     #             }
#     #             file_object_json = json.dumps(file_object)
#     #             handle.write(file_object_json)
#     #
#     #     except Exception as e:
#     #         print("169 Exception occurred", str(e))
#
#     # Function to parse the text content from the url and get outgoing links from the current page
#     def parse_content(self, content, url):
#
#         html_parser = MyHTMLParser(url, self.base_url)
#         html_parser.feed(content)
#         links = html_parser.get_data()
#         return links
#
#     # Function to create two maps (url->id and id->url) and write to file system
#     def create_id_url_map(self):
#         try:
#             urls = None
#             for root, dirs, files in os.walk(WebCrawler.file_contents_path):
#                 urls = files
#
#             if urls is None:
#                 return
#
#             for url_file in urls:
#                 with open(os.path.join(WebCrawler.file_contents_path, url_file)) as handle:
#                     url = json.loads(handle.read())['url']
#                     url_id = url_file
#                     self.url_to_code[url] = url_id
#                     self.code_to_url[url_id] = url
#
#             with open(self.url_to_code_map_path, "w+") as handle:
#                 handle.write(json.dumps(self.url_to_code))
#
#             with open(self.code_to_url_map_path, "w+") as handle:
#                 handle.write(json.dumps(self.code_to_url))
#
#         except Exception as e:
#             print("203 Exception occurred", str(e))
#
#
# c = WebCrawler()
# c.start_crawling()
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
    number_of_threads = 25
    threads_executor = ""
    visited_urls = None
    atomic_counter = AtomicCounter()
    file_contents_path = os.path.join(r'E:\IR\Project - Copy', r'url_contents')
    base_url = "uic.edu"
    url_with_outgoing_links = dict()
    task_list = list()

    url_to_code_map_path = os.path.join(r'E:\IR\Project - Copy', 'Computations', 'url_code_map.json')
    code_to_url_map_path = os.path.join(r'E:\IR\Project - Copy', 'Computations', 'code_to_url_map.json')

    def __init__(self):
        self.code_to_url = dict()
        self.url_to_code = dict()
        self.queue = Queue()
        self.threads_executor = ThreadPoolExecutor(max_workers=self.number_of_threads, thread_name_prefix="test")
        self.visited_urls = set()
        if not os.path.exists(self.file_contents_path):
            os.makedirs(self.file_contents_path)

    def start_crawling(self):
        try:
            self.queue.put(self.root_url)
            while True:
                #
                if self.atomic_counter.get_value() >= self.pages_to_crawl:
                    self.threads_executor.shutdown(cancel_futures=True)
                    break

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
                    print(e)
                if url in self.visited_urls:
                    continue
                self.visited_urls.add(url)
                if self.atomic_counter.get_value() <= self.pages_to_crawl:
                    task = self.threads_executor.submit(self.process_url, url)
                    self.task_list.append(task)

                # task.add_done_callback(self.get_links_from_url_content)
                # self.write_content_to_persistent_storage(url)

            print(self.url_with_outgoing_links)
        except Exception as e:
            print(e)

    def process_url(self, url):
        try:
            # print(threading.current_thread().name)
            if self.atomic_counter.get_value() >= self.pages_to_crawl:
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
            return json.dumps(value)
        finally:
            return json.dumps(value)

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
        exclusion_filter = '.com'
        html_parser = MyHTMLParser(self.root_url, self.base_url)
        html_parser.feed(content)
        links = html_parser.get_data()
        return links

    def write_links_to_persistent_storage(self, url, links):
        pass

    #     # Function to create two maps (url->id and id->url) and write to file system
    def create_id_url_map(self):
        try:
            urls = None
            for root, dirs, files in os.walk(WebCrawler.file_contents_path):
                urls = files

            if urls is None:
                return

            for url_file in urls:
                with open(os.path.join(WebCrawler.file_contents_path, url_file)) as handle:
                    url = json.loads(handle.read())['url']
                    url_id = url_file
                    self.url_to_code[url] = url_id
                    self.code_to_url[url_id] = url

            with open(self.url_to_code_map_path, "w+") as handle:
                handle.write(json.dumps(self.url_to_code))

            with open(self.code_to_url_map_path, "w+") as handle:
                handle.write(json.dumps(self.code_to_url))

        except Exception as e:
            print("Exception occurred ", e)

c = WebCrawler()
c.create_id_url_map()
