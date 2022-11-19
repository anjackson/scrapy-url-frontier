import scrapy
from scrapy.http.request import Request
from scrapy.http import Response, TextResponse
from scrapy.linkextractors import LinkExtractor


class ExampleSpider(scrapy.Spider):
    name = 'example'
#    allowed_domains = [
#        'data.webarchive.org.uk',
#        'acid.matkelly.com',
#        'ibnesayeed.github.io',
#        'anjackson.net',
#        'example.com',
#        'example.org',
#    ]
#    start_urls = [
#        'http://data.webarchive.org.uk/crawl-test-site/',
#        'http://acid.matkelly.com/',
#        'https://ibnesayeed.github.io/acrts/',
#        #'https://anjackson.net',
#   ]

    link_extractor = LinkExtractor()

    def parse(self, response: Response):
        if isinstance(response, TextResponse):
            for link in self.link_extractor.extract_links(response):
                yield Request(link.url, callback=self.parse)


