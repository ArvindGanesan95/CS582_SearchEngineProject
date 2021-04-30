from Crawler.WebCrawler import SpiderCrawler

if __name__ == '__main__':
    try:
        crawler = SpiderCrawler(pages_to_crawl=100, number_of_workers=20)
        crawler.crawl()
    except Exception as e:
        print(e)
