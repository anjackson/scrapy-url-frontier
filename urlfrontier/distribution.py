#
# 
#

import re
import json
import scrapy
import logging
from urllib.parse import urlparse
from uhashring import HashRing
from urlfrontier.grpc.urlfrontier_pb2 import AnyCrawlID, GetParams, URLInfo, URLItem, DiscoveredURLItem, KnownURLItem, StringList, QueueWithinCrawlParams, Pagination, Local, DeleteCrawlMessage
from w3lib.url import canonicalize_url


logger = logging.getLogger(__name__)

#  Convert Request to URLInfo
def request_to_urlInfo(request: scrapy.Request, crawlID=None, queue=None, encoder=None, keep_fragments=False):

    # Canonicalize the URL for the unique key:
    canon_url = canonicalize_url(request.url, keep_fragments=keep_fragments)

    if encoder is not None:
        encoded_request = encoder.encode_request(request)

        return URLInfo(
            # URLs placed in canonical form to avoid duplicate requests:
            url=canon_url,
            # key=None means frontier default queue key
            key=queue, 
            crawlID=request.meta.get('spiderid', crawlID),
            metadata={'scrapy_request': StringList(values=[encoded_request])}
        )
    else:
        metadata = {}
        metadata['meta'] = StringList(values=[ json.dumps(request.meta) ])
        metadata['original_url'] = StringList(values=[ request.url ])
        return URLInfo(
            # URLs placed in canonical form to avoid duplicate requests:
            url=canon_url,
            # queue=None means frontier default queue key
            key=queue,
            crawlID=request.meta.get('spiderid', crawlID),
            metadata=metadata
        )

def urlInfo_to_request(uf: URLInfo, decoder=None):
    if 'scrapy_request' in uf.metadata:
        encoded_request = uf.metadata['scrapy_request'].values[0]
        return decoder.decode_request(encoded_request)
    else:
        # Override URL with metadata URL if set:
        if 'original_url' in uf.metadata:
            original_url = uf.metadata['original_url'].values[0]
        else:
            original_url = uf.url
        if 'meta' in uf.metadata:
            meta = json.loads(uf.metadata['meta'].values[0])
        else:
            meta = {}
        # Build the Request object:
        return scrapy.Request(url=original_url, meta=meta)


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

    def matches_spider_id(self, request: scrapy.Request):
        # Check the ID associated with this spider matches the one allocated to the request:
        if self.get_spider_partition() == request.meta.get('spiderid', None):
            return True
        else:
            return False

    def request_to_put_url(self, url: str, meta=None, encoder=None, known=False, refetch_date=0):
        request = scrapy.Request(url, meta=meta)
        request = self.set_spider_id(request)
        urlInfo = request_to_urlInfo(request, encoder=encoder)
        logger.info(f"URLInfo {urlInfo} with CrawlID {urlInfo.crawlID}")
        if known:
            return URLItem(known=KnownURLItem(info=urlInfo, refetchable_from_date=refetch_date))
        else:
            return URLItem(discovered=DiscoveredURLItem(info=urlInfo))
