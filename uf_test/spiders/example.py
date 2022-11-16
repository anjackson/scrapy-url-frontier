import scrapy
from scrapy.http.request import Request
from scrapy.linkextractors import LinkExtractor


class ExampleSpider(scrapy.Spider):
    name = 'example'
    allowed_domains = ['data.webarchive.org.uk']
    start_urls = ['http://data.webarchive.org.uk/crawl-test-site/']

    link_extractor = LinkExtractor()

    def parse(self, response):
        for link in self.link_extractor.extract_links(response):
            yield Request(link.url, callback=self.parse)


