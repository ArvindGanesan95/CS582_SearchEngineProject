from abc import ABC

import scrapy
from scrapy.spiders import CrawlSpider


class MySpider(CrawlSpider, ABC, ABC):
    name = "example.com"
    allowed_domains = ['uic.edu']
    start_urls = ['https://www.cs.uic.edu']

    rules = (

        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        Rule(LinkExtractor(), callback='parse_item'),
    )

    def parse_item(self, response):
        self.logger.info('Hi, this is an item page! %s', response.url)
        item = scrapy.Item()
        # item['id'] = response.xpath('//td[@id="item_id"]/text()').re(r'ID: (\d+)')
        # item['name'] = response.xpath('//td[@id="item_name"]/text()').get()
        # item['description'] = response.xpath('//td[@id="item_description"]/text()').get()
        # item['link_text'] = response.meta['link_text']
        url = response.xpath('//td[@id="additional_data"]/@href').get()
        return response.follow(url, self.parse_additional_page, cb_kwargs=dict(item=item))

    def parse_additional_page(self, response, item):
        item['additional_data'] = response.xpath('//p[@id="additional_data"]/text()').get()
        return item
