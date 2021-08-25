import time
import codecs
import pickle
from typing import Optional, Type, TypeVar
from twisted.internet.defer import Deferred

import grpc

from scrapy.crawler import Crawler
from scrapy.spiders import Spider
from scrapy import signals
from scrapy.http.request import Request
from scrapy.http.response import Response
#from scrapy.core.scheduler import BaseScheduler, SchedulerTV
from scrapy.utils.job import job_dir
from scrapy.utils.misc import create_instance, load_object

from urlfrontier_pb2_grpc import URLFrontierStub
from urlfrontier_pb2 import GetParams, URLInfo, URLItem, DiscoveredURLItem, KnownURLItem, StringList

#class URLFrontierScheduler(BaseScheduler):
# BaseScheduler appears not to be release yet...
class URLFrontierScheduler():

    def __init__(
        self,
        endpoint,
        debug: bool = False,
        stats=None,
        crawler: Optional[Crawler] = None,
    ):
        self.endpoint = endpoint
        self.debug = debug
        self.stats = stats
        self.crawler = crawler
 
    #def from_crawler(cls: Type[SchedulerTV], crawler) -> SchedulerTV:
    @classmethod
    def from_crawler(cls, crawler):
        """
        Factory method, initializes the scheduler with arguments taken from the crawl settings
        """
        scheduler = cls(
            endpoint=crawler.settings['SCHEDULER_URLFRONTIER_ENDPOINT'],
            debug=crawler.settings.getbool('SCHEDULER_DEBUG'),
            stats=crawler.stats,
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
        # TODO Convert Request to URLInfo
        print("Enqueuing "+ str(request) + " " + request.url)

        # TODO Replace with simpler encoding of subset of fields:
        #scrapy_request = pickled = codecs.encode(pickle.dumps(request), "base64").decode()
        
        urlinfo = URLInfo(
            url=request.url,
            key=None, # Use frontier default
            #metadata={'scrapy_request': StringList(values=[scrapy_request])}
        )
        if request.dont_filter:
            now_ts = int(time.time())
            uf_request = URLItem(known=KnownURLItem(info=urlinfo, refetchable_from_date=now_ts))
        else:
            uf_request = URLItem(discovered=DiscoveredURLItem(info=urlinfo))
        return self._PutURLs(uf_request)


    def next_request(self) -> Optional[Request]:
        """
        Return the next :class:`~scrapy.http.Request` to be processed, or ``None``
        to indicate that there are no requests to be considered ready at the moment.

        Returning ``None`` implies that no request from the scheduler will be sent
        to the downloader in the current reactor cycle. The engine will continue
        calling ``next_request`` until ``has_pending_requests`` is ``False``.
        """
        # Ask for a single URL:
        uf_request = GetParams(max_urls_per_queue=1, max_queues=1)
        for uf_response in self._stub.GetURLs(uf_request):
            print("recv request from URL Frontier url=%s, metadata=%s" % (uf_response.url, uf_response.metadata))
            # Convert URLInfo into a Request
            # and return it
            if 'scrapy_request' in uf_response.metadata:
                scrapy_request = uf_response.metadata['scrapy_request'].values[0]
                return pickle.loads(codecs.decode(scrapy_request.encode(), "base64"))
            else:
                return Request(url=uf_response.url)

        return None


    def _record_response(self, response, request, spider):
        ### Signal handler to record downloader outcomes
        # https://docs.scrapy.org/en/latest/topics/signals.html#response-downloaded
        print("Recording response...")
        # Convert Response to KnownURLItem
        urlinfo = URLInfo(
            url=request.url
        )
        uf_request = URLItem(known=KnownURLItem(info=urlinfo, refetchable_from_date=0))
        return self._PutURLs(uf_request)

    def _PutURLs(self, uf_request):
        for uf_response in self._stub.PutURLs(iter([uf_request])):
            print("recv from PUT url=%s, message=%s" %
              (uf_response.value, str(uf_response)))
              # TODO ack
            return True
