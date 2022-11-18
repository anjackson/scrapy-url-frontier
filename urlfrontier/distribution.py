#
# 
#

import re
import logging
from uhashring import HashRing

logger = logging.getLogger(__name__)

class HashRingDistributor():
    # 

    def __init__(self, crawler) -> None:
        """
        The Scrapy crawler instance used to determine the settings.
        """
        self.nodes = []
        self.spider_name = crawler.spider.name
        spider_partition_id = crawler.settings.get('SPIDER_PARTITION_ID', None)
        if spider_partition_id is None:
            # Don't partition if this field is not set:
            self.spider_id = None
            self.nodes.append(self.spider_name)
        else:
            # Validate the X/N string:
            pattern = re.compile("^\d+\/\d+$")
            if not pattern.match(spider_partition_id):
                raise Exception("SPIDER_PARTITION_ID must be in the form X/N, e.g. 1/2.")
            # Parse the partition ID
            spider_id, num_spiders = spider_partition_id.split('/')
            self.spider_id = int(spider_id)
            self.num_spiders = int(num_spiders)
            if self.spider_id <= 0 or self.spider_id > self.num_spiders:
                raise Exception("SPIDER_PARTITION_ID must specify an ID between 1 and N.")
            self.partition_separator = crawler.settings.get('PARTITION_SEPARATOR', ".")
            for i in range(1, self.num_spiders + 1):
                self.nodes.append(f"{self.spider_name}{self.partition_separator}{i}")

        # Store the resulting hash ring:
        self.hash_ring = HashRing(self.nodes)

    def get_spider_partition(self):
        if self.spider_id:
            return f"{self.spider_name}{self.partition_separator}{self.spider_id}"
        else:
            return self.spider_name

    def set_spider_id(self, request, spider):
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

