"""
# Docstring for Scrapt.tutorial.spiders.amazon_spider

import scrapy
from tutorial.items import AmazonItem

class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    start_urls = [
        'https://www.amazon.com/s?k=converse&i=fashion-boys-intl-ship'
    ]

    def parse(self, response):
        products = response.css('div.s-result-item[data-component-type="s-search-result"]')

        for product in products:
            item = AmazonItem()
            product_name = response.css('h2.s-access-title::text').extract()
            product_price = response.css('span.sx-price-whole::text').extract()
            item['product_name'] = product_name
            item['product_price'] = product_price
            yield item

"""



import scrapy
from tutorial.items import AmazonItem

class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    start_urls = [
        'https://www.amazon.com/s?k=converse&i=fashion-boys-intl-ship'
    ]

    def parse(self, response):
        products = response.css('div.s-result-item[data-component-type="s-search-result"]')

        for product in products:
            item = AmazonItem()

            product_name = product.css('h2 span::text').get()
            product_price = product.css('span.a-price > span.a-offscreen::text').get()

            item['product_name'] = product_name
            item['product_price'] = product_price

            yield item
