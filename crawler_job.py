"""
Submitted by,
Arvind Ganesan
NETID: aganes25@uic.edu
"""
import json

from Crawler.WebCrawler import SpiderCrawler

if __name__ == '__main__':
    try:
        crawler = SpiderCrawler(pages_to_crawl=3000, number_of_workers=20)
        crawler.crawl()
    except Exception as e:
        print(e)

