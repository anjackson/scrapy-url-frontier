# -*- coding: utf-8 -*-
from __future__ import absolute_import
from frontera import Backend
from frontera.utils.misc import load_object
from frontera.core.models import Request as FRequest
import logging
import six
import time
import grpc

from scrapy.http.request import Request

from urlfrontier_pb2_grpc import URLFrontierStub
from urlfrontier_pb2 import GetParams, URLInfo, URLItem, DiscoveredURLItem, KnownURLItem, StringList


class URLFrontierBackend(Backend):
    def __init__(self, manager):
        settings = manager.settings
        self.endpoint = settings.get('FRONTERA_URLFRONTIER_ENDPOINT', 'localhost:7071')
        codec_path = settings.get('FRONTERA_URLFRONTIER_CODEC')
        decoder_cls = load_object(codec_path+".Decoder")
        encoder_cls = load_object(codec_path+".Encoder")
        store_content = settings.get('STORE_CONTENT')
        self._encoder = encoder_cls(manager.request_model, send_body=store_content)
        self._decoder = decoder_cls(manager.request_model, manager.response_model)
        #self.partition_id = int(settings.get('SPIDER_PARTITION_ID'))
        #if self.partition_id < 0 or self.partition_id >= settings.get('SPIDER_FEED_PARTITIONS'):
        #    raise ValueError("Spider partition id cannot be less than 0 or more than SPIDER_FEED_PARTITIONS.")
        
        self._logger = logging.getLogger("urlfrontier-backend")
        
        #self._logger.info("Consuming from partition id %d", self.partition_id)

    @classmethod
    def from_manager(cls, manager):
        return cls(manager)

    def frontier_start(self):
        self._logger.warn("Starting...")
        self._channel = grpc.insecure_channel(self.endpoint)
        self._stub = URLFrontierStub(self._channel)
        self._logger.warn("Started...")

    def frontier_stop(self):
        self._logger.warn("Stopping...")
        if self._channel:
            self._channel.close()

    def add_seeds(self, seeds):
        self._logger.warn("Adding seeds " + str(seeds))
        for seed in seeds:
            self._logger.warn("Adding seed "+ seed)
            seed_request = Request(url=seed, meta={b'frontier_request'})
            encoded_request = self._encoder.encode_request(seed_request)
            urlinfo = URLInfo(
                url=seed,
                key=None, # Use frontier default
                metadata={'scrapy_request': StringList(values=[encoded_request])}
            )
            now_ts = int(time.time())
            uf_request = URLItem(known=KnownURLItem(info=urlinfo, refetchable_from_date=now_ts))
            self._PutURLs(uf_request)

    def page_crawled(self, response):
        self._logger.warn("page_crawled...")
        urlinfo = URLInfo(
            url=response.request.url
        )
        uf_request = URLItem(known=KnownURLItem(info=urlinfo, refetchable_from_date=0))
        self._PutURLs(uf_request)

    def links_extracted(self, request, links):
        self._logger.warn("links_extracted...")
        for link in links:
            print("Enqueuing "+ str(link) + " " + link.url)

            # TODO Replace with simpler encoding of subset of fields:
            link_request = Request(link.url, meta={b'frontier_request': FRequest(link.url)})
            encoded_request = self._encoder.encode_request(link_request)
            
            urlinfo = URLInfo(
                url=link.url,
                key=None, # Use frontier default
                metadata={'scrapy_request': StringList(values=[encoded_request])}
            )
            uf_request = URLItem(discovered=DiscoveredURLItem(info=urlinfo))
            self._PutURLs(uf_request)

    def request_error(self, page, error):
        self._logger.warn("request_error...")
        self._logger.info(self._encoder.encode_request_error(page, error))

    def get_next_requests(self, max_n_requests, **kwargs):
        self._logger.warn("get_next_requests...")
       # Ask for a single URL:
        uf_request = GetParams(max_urls_per_queue=1, max_queues=max_n_requests)
        requests = []
        for uf_response in self._stub.GetURLs(uf_request):
            print("recv request from URL Frontier url=%s, metadata=%s" % (uf_response.url, uf_response.metadata))
            # Convert URLInfo into a Request
            # and return it
            if 'scrapy_request' in uf_response.metadata:
                encoded_request = uf_response.metadata['scrapy_request'].values[0]
                requests.append(self._decoder.decode_request(encoded_request))
            else:
                requests.append(Request(url=uf_response.url))

        return requests

    def finished(self):
        return False

    @property
    def metadata(self):
        return None

    @property
    def queue(self):
        return None

    @property
    def states(self):
        return None

