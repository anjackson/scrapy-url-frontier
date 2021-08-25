import scrapy
from scrapy.http.request import Request
from scrapy.linkextractors import LinkExtractor


class ExampleSpider(scrapy.Spider):
    name = 'example'
    allowed_domains = ['example.com']
    start_urls = ['http://example.com/']

    link_extractor = LinkExtractor()

    def parse(self, response):
        for link in self.link_extractor.extract_links(response):
            yield Request(link.url, callback=self.parse)