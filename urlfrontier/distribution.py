#
# 
#

import re
import scrapy
import logging
from urllib.parse import urlparse
from uhashring import HashRing

logger = logging.getLogger(__name__)

class HashRingDistributor():
    """
    """
    
    def __init__(self, spider_name, spider_id, num_spiders, separator=".") -> None:
        """
        Setup the hash ring, as needed.
        """
        self.nodes = []
        self.spider_name = spider_name
        self.num_spiders = num_spiders
        self.partition_separator = separator
        if spider_id is None:
            # Don't partition if this field is not set:
            self.spider_id = None
            self.nodes.append(self.spider_name)
        else:
            self.spider_id = spider_id
            for i in range(1, self.num_spiders + 1):
                self.nodes.append(f"{self.spider_name}{self.partition_separator}{i}")

        # Store the resulting hash ring:
        self.hash_ring = HashRing(self.nodes)

    def get_spider_partition(self):
        if self.spider_id:
            return f"{self.spider_name}{self.partition_separator}{self.spider_id}"
        else:
            return self.spider_name

    def set_spider_id(self, request: scrapy.Request, spider=None):
        # If this has been set explicitly, don't override it:
        if 'spiderid' in request.meta:
            return request

        if spider is not None:
            # Get slot/queue key for this downloader:
            # n.b. this is an internal API so may shift between versions of Scrapy.
            # https://github.com/scrapy/scrapy/blob/29bf7f5a6c8460e030e465351d2e6d38acf22f3d/scrapy/core/downloader/__init__.py#L108
            slot_key = spider.crawler.engine.downloader._get_slot_key(request, spider)
        else:
            slot_key = urlparse(request.url).hostname

        logger.info(f"Got slot key {slot_key} for {request}")

        # Set the destination spider ID by hashing the slot key:
        request.meta['spiderid'] = self.hash_ring.get_node(slot_key)
        logger.info(f"Destination Spider ID set to {request.meta['spiderid']}")

        return request

