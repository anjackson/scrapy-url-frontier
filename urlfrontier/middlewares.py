#
# 
#

import logging
from scrapy import signals, Request
from uhashring import HashRing

logger = logging.getLogger(__name__)

class HashRingDistributorSpiderMiddleware():
    # 

    def __init__(self, spider_name, num_spiders) -> None:
        self.nodes = []
        self.spider_name = spider_name
        self.num_spiders = int(num_spiders)
        for i in range(0, num_spiders):
            self.nodes.append(f"{spider_name}-{i}")
        self.hash_ring = HashRing(self.nodes)

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        spider_name = crawler.spider.name
        num_spiders = crawler.settings.get('HASH_RING_DISTRIBUTOR_NUM_SPIDERS', 1)
        s = cls(spider_name, num_spiders)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            if isinstance(i, Request):
                i = self._set_spider_id(i, spider)
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield self._set_spider_id(r, spider)

    def spider_opened(self, spider):
        spider.logger.info('Spider opened, with request distribution across spiders called: %s' % self.nodes)


    def _set_spider_id(self, request, spider):
        # If this has been set explicitly, don't override it:
        if 'spiderid' in request.meta:
            return request

        # Get slot/queue key for this downloader:
        # n.b. this is an internal API so may shift between versions of Scrapy.
        # https://github.com/scrapy/scrapy/blob/29bf7f5a6c8460e030e465351d2e6d38acf22f3d/scrapy/core/downloader/__init__.py#L108
        slot_key = spider.crawler.engine.downloader._get_slot_key(request, spider)
        spider.logger.info(f"Got slot key {slot_key} for {request}")

        # Set the destination spider ID by hashing the slot key:
        request.meta['spiderid'] = self.hash_ring.get_node(slot_key)
        spider.logger.info(f"Destination Spider ID set to {request.meta['spiderid']}")

        return request

