import scrapy

class AmazonItem(scrapy.Item):
    product_name = scrapy.Field()
    product_price = scrapy.Field()
