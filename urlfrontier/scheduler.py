# 

import re
import time
import json
import logging
from typing import Optional, Type, TypeVar

from twisted.internet.defer import Deferred

from scrapy.crawler import Crawler
from scrapy.spiders import Spider
from scrapy import signals
from scrapy.http.request import Request
from scrapy.http.response import Response
#from scrapy.core.scheduler import BaseScheduler, SchedulerTV
from scrapy.utils.job import job_dir
from scrapy.utils.misc import create_instance, load_object

import grpc
from urlfrontier.grpc.urlfrontier_pb2_grpc import URLFrontierStub
from urlfrontier.grpc.urlfrontier_pb2 import GetParams, URLInfo, URLItem, DiscoveredURLItem, KnownURLItem, StringList, QueueDelayParams
from urlfrontier.distribution import HashRingDistributor, urlInfo_to_request, request_to_urlInfo

#class URLFrontierScheduler(BaseScheduler):
# BaseScheduler appears not to be release yet...
class URLFrontierScheduler():
    """

    SCHEDULER_URLFRONTIER_DEFAULT_DELAY_REQUESTABLE

    The time (in seconds) to wait before the URL Frontier is allowed to send a given URL out again to re-try to crawl it.
    This is set to a long period (10 minutes), as it should only be relevant in cases where the spider crashes.

    SCHEDULER_URLFRONTIER_CODEC

    Can use Frontera's string encoding classes. e.g. 

    SCHEDULER_URLFRONTIER_CODEC='frontera.contrib.backends.remote.codecs.json'

    """

    def __init__(
        self,
        crawler: Optional[Crawler] = None,
    ):
        self.endpoint=crawler.settings['SCHEDULER_URLFRONTIER_ENDPOINT']
        self.debug=crawler.settings.getbool('SCHEDULER_DEBUG')
        self.stats = crawler.stats
        self.crawler = crawler
        self.default_delay_requestable = crawler.settings.getint('SCHEDULER_URLFRONTIER_DEFAULT_DELAY_REQUESTABLE', 10*60*60)
        # Setting this to anything other that 1 will not work properly right now as next_request can only return one Request:
        self.max_queues = crawler.settings.getint('SCHEDULER_URLFRONTIER_GETURLS_MAX_QUEUES', 1)

        # Hash Ring Distribution configuration:
        self.spider_name = crawler.spider.name
        spider_partition_id = crawler.settings.get('SPIDER_PARTITION_ID', None)
        self.partition_separator = crawler.settings.get('PARTITION_SEPARATOR', ".")
        if spider_partition_id is None:
            # Don't partition if this field is not set:
            spider_i = None
            self.num_spiders = 1
        else:
            # Validate the X/N string:
            pattern = re.compile("^\d+\/\d+$")
            if not pattern.match(spider_partition_id):
                raise Exception("SPIDER_PARTITION_ID must be in the form X/N, e.g. 1/2.")
            # Parse the partition ID
            spider_i, num_spiders = spider_partition_id.split('/')
            spider_i = int(spider_i)
            self.num_spiders = int(num_spiders)
            if spider_i <= 0 or spider_i > self.num_spiders:
                raise Exception("SPIDER_PARTITION_ID must specify an ID between 1 and N.")
        # Set up hash ring based on these parameters:
        self.distributor = HashRingDistributor(
            spider_name=self.spider_name,
            spider_id=spider_i,
            num_spiders=self.num_spiders,
            separator=self.partition_separator,
            )
        self.spider_id = self.distributor.get_spider_partition()

        self._logger = logging.getLogger("urlfrontier-scheduler")
        # Set up codec (supporting Frontera codecs):
        codec_path = crawler.settings.get('SCHEDULER_URLFRONTIER_CODEC', None)
        if codec_path is not None:
            decoder_cls = load_object(codec_path+".Decoder")
            encoder_cls = load_object(codec_path+".Encoder")
            store_content = crawler.settings.get('STORE_CONTENT')
            self._encoder = encoder_cls(Request, send_body=store_content)
            self._decoder = decoder_cls(Request, Response)
        else:
            self._encoder = None
            self._decoder = None
        
 
    #def from_crawler(cls: Type[SchedulerTV], crawler) -> SchedulerTV:
    @classmethod
    def from_crawler(cls, crawler):
        """
        Factory method, initializes the scheduler with arguments taken from the crawl settings
        """
        scheduler = cls(
            crawler=crawler,
        )
        # Register signal handler to record outcomes:
        crawler.signals.connect(scheduler._record_response, signals.response_downloaded)
        return scheduler

    def open(self, spider: Spider) -> Optional[Deferred]:
        """
        Called when the spider is opened by the engine. It receives the spider
        instance as argument and it's useful to execute initialization code.

        :param spider: the spider object for the current crawl
        :type spider: :class:`~scrapy.spiders.Spider`
        """
        self._channel = grpc.insecure_channel(self.endpoint)
        self._stub = URLFrontierStub(self._channel)
        # Override the 1s defaultDelayForQueues:
        self._stub.SetDelay(
            QueueDelayParams(
                key=None,
                crawlID=self.spider_id, # Seems this MUST be set
                delay_requestable=1,
                local=False,
            )
        )


    def close(self, reason: str) -> Optional[Deferred]:
        """
        Called when the spider is closed by the engine. It receives the reason why the crawl
        finished as argument and it's useful to execute cleaning code.

        :param reason: a string which describes the reason why the spider was closed
        :type reason: :class:`str`
        """
        if self._channel:
            self._channel.close()


    def has_pending_requests(self) -> bool:
        """
        ``True`` if the scheduler has enqueued requests, ``False`` otherwise
        """
        # This frontier never ends...
        return True


    def enqueue_request(self, request: Request) -> bool:
        """
        Process a request received by the engine.

        Return ``True`` if the request is stored correctly, ``False`` otherwise.

        If ``False``, the engine will fire a ``request_dropped`` signal, and
        will not make further attempts to schedule the request at a later time.
        For reference, the default Scrapy scheduler returns ``False`` when the
        request is rejected by the dupefilter.
        """
        request = self.distributor.set_spider_id(request, self.crawler.spider)
        urlInfo = request_to_urlInfo(request, encoder=self._encoder,
            crawlID=request.meta['spiderid'])
        self.crawler.stats.inc_value('urlfrontier/enqueue_request_count')
        if request.dont_filter:
            now_ts = int(time.time())
            uf_request = URLItem(known=KnownURLItem(info=urlInfo, refetchable_from_date=now_ts))
            self.crawler.stats.inc_value('urlfrontier/enqueue_request_count/dont_filter')
            self._logger.info("PutURL dont_filter request=" + str(request))
            return self._PutURLs(uf_request, "known_dont_filter")
        else:
            uf_request = URLItem(discovered=DiscoveredURLItem(info=urlInfo))
            self._logger.info("PutURL request=" + str(request))
            return self._PutURLs(uf_request, "discovered")


    def next_request(self) -> Optional[Request]:
        """
        Return the next :class:`~scrapy.http.Request` to be processed, or ``None``
        to indicate that there are no requests to be considered ready at the moment.

        Returning ``None`` implies that no request from the scheduler will be sent
        to the downloader in the current reactor cycle. The engine will continue
        calling ``next_request`` until ``has_pending_requests`` is ``False``.
        """
        # Ask for URLs, no more than one per queue:
        g = GetParams(
            max_urls_per_queue = 1,
            max_queues = self.max_queues,
            delay_requestable = self.default_delay_requestable,
            #key = None,
            crawlID = self.spider_id
        )
        self._logger.debug(f"Looking for URLs under crawlID = {self.spider_id}...")
        for uf_response in self._stub.GetURLs(g):
            self._logger.debug("GetURLs rx url=%s, metadata=%s" % (uf_response.url, uf_response.metadata))
            self.crawler.stats.inc_value('urlfrontier/get_urls_count')            
            # Convert URLInfo into a Request and return it
            return urlInfo_to_request(uf_response, decoder=self._decoder)

        return None

    def _record_response(self, response, request, spider):
        ### Signal handler to record downloader outcomes
        # https://docs.scrapy.org/en/latest/topics/signals.html#response-downloaded
        # i.e. this records the outcome of the download.
        self._logger.debug(f"Recording crawl outcome request={request} response={response}")
        # Set the partition:
        self.distributor.set_spider_id(request, self.crawler.spider)
        # Convert Response to KnownURLItem
        urlInfo = request_to_urlInfo(request, encoder=self._encoder, crawlID=request.meta['spiderid'])
        uf_request = URLItem(known=KnownURLItem(info=urlInfo, refetchable_from_date=0))
        return self._PutURLs(uf_request, "known")

    def _PutURLs(self, uf_request, urlInfoKind):
        for uf_response in self._stub.PutURLs(iter([uf_request])):
            # Status 0 OK, 1 Skipped, 2 FAILED
            self._logger.debug("PutURL ID=%s Status=%i" % (uf_response.ID, uf_response.status))
            self.crawler.stats.inc_value(f'urlfrontier/put_urls_{urlInfoKind}_count')
            if uf_response.status == 0:
                self.crawler.stats.inc_value(f'urlfrontier/put_urls_{urlInfoKind}_count/ok')
            elif uf_response.status == 1:
                self.crawler.stats.inc_value(f'urlfrontier/put_urls_{urlInfoKind}_count/skipped')
            elif uf_response.status == 2:
                self.crawler.stats.inc_value(f'urlfrontier/put_urls_{urlInfoKind}_count/failed')
                # FIXME Throw an exception in this case?
                
            return True
        return False

