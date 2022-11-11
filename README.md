scrapy-url-frontier
===================

Just attempting to test integration with URL Frontier.

Steps Taken
-----------

Build and run the URL Frontier, as per the instructions. Or, use the supplied Docker Compose file:

    docker compose up urlfrontier

In another terminal...

    sudo apt-get install libffi-dev

Set up a virtualenv and installed all requirements (`scrapy`, `scrapy-playwright`, `grpc` and `grpc-tools`).

Generated stubs with:

    curl -o urlfrontier/grpc/urlfrontier.proto https://raw.githubusercontent.com/crawler-commons/url-frontier/2.3/API/urlfrontier.proto
    python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. urlfrontier/grpc/urlfrontier.proto

Then ran a simple spider with:

    scrapy crawl example

The crawl runs at this point, and because `allowed_domains` is unset, quickly widens in scope to cover a number of hosts.

If the crawl is killed and restarted, the crawl will continue to get the URLs that were discovered but not crawled.

But the crawl will not make a full restart, i.e. the URL Frontier acts as a dupe filter. However, seed URLs get marked as `dont_filter` and this is implemented here as allowing immediate recrawl, so seeds will be re-fetched on restarts.

So, it basically works, but will require much more work to function properly.  This includes (at least):

- [x] Consider implementing as a [Frontera](https://frontera.readthedocs.io/) [back-end](https://frontera.readthedocs.io/en/latest/topics/frontier-backends.html) - this will handle a lot of the management logic around encoding properties, stats, etc. but is more complex to implement
- [x] Map any important properties and metadata from Scrapy's `Request` class to `URLInfo.metadata` and back again (see notes below).
- [x] Consider supporting `dont_filter` by enqueuing those URLs as `KnownURLItem` instances with the `refetchable_from_date` set appropriately. (n.b. "The default implementation [of start_requests()] generates Request(url, dont_filter=True) for each url in start_urls.")
- [ ] Canonicalize the URL key (which is used for de-dup) but leave the `scrapy-request` URL unchanged.
- [x] Check `crawl-delay` works, i.e. is it handled in Scrapy, or do we need to be using `SetDelay` somehow?
- [ ] Setup the full via-WARC-writing-proxy Docker Stack.
- [x] Consider schemes to partition queues across multiple instances of Scrapy. i.e. if a Scrapy knows it is Scrapy 1 of 10, then periodically list the queues and assign a stable subset to each Scrapy (e.g. hash the queue keys and distribute those - as we did for Kafka+H3).
- [ ] Consider making use of the URL Frontier support for additional stats.
- [x] ~~Add a Prometheus endpoint to the URL Frontier service.~~ Already exists!


Serialisation is an interesting issue. The `Request` can have references to Callable functions, and even to thread locks, so can't necessarily be pickled as-is.  We can follow Frontera's lead and [just keep these critical elements](https://github.com/scrapinghub/frontera/blob/84f9e1034d2868447db88e865596c0fbb32e70f6/frontera/contrib/backends/remote/codecs/json.py#L58-L63) (while noting that `dont_filter` is not included at present, may be missing `formdata` or `data` from form or JSON requests). But we must note that this will drop any callbacks attached to specific requests (the same as for Frontera, which [throws an error if you break this rule](https://github.com/scrapinghub/scrapy-frontera/blob/fab14232bedbe89b781479a13918eb3166a1564e/scrapy_frontera/scheduler.py#L29-L37)).

It would be possible to implement this as a Frontera backend, although the Distributed model includes a lot of assumptions about deployment and consequential complexity.  A partial implementation is included, but e.g.

```
21:03 $ python -m frontera.utils.add_seeds --config uf_test.frontera.settings --seeds-file seeds.txt 
[__main__] Starting local seeds addition from file seeds.txt
INFO:__main__:Starting local seeds addition from file seeds.txt
INFO:manager:--------------------------------------------------------------------------------
INFO:manager:Starting Frontier Manager...
WARNING:urlfrontier-backend:Starting...
WARNING:urlfrontier-backend:Started...
INFO:manager:Frontier Manager Started!
INFO:manager:--------------------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/Cellar/python@3.9/3.9.6/Frameworks/Python.framework/Versions/3.9/lib/python3.9/runpy.py", line 197, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "/usr/local/Cellar/python@3.9/3.9.6/Frameworks/Python.framework/Versions/3.9/lib/python3.9/runpy.py", line 87, in _run_code
    exec(code, run_globals)
  File "/Users/anj/Documents/workspace/scrapy-url-frontier/venv/lib/python3.9/site-packages/frontera/utils/add_seeds.py", line 44, in <module>
    run_add_seeds(settings, args.seeds_file)
  File "/Users/anj/Documents/workspace/scrapy-url-frontier/venv/lib/python3.9/site-packages/frontera/utils/add_seeds.py", line 20, in run_add_seeds
    manager.add_seeds(fh)
  File "/Users/anj/Documents/workspace/scrapy-url-frontier/venv/lib/python3.9/site-packages/frontera/core/manager.py", line 495, in add_seeds
    self.strategy.read_seeds(seeds_file)
  File "/Users/anj/Documents/workspace/scrapy-url-frontier/venv/lib/python3.9/site-packages/frontera/strategy/basic.py", line 10, in read_seeds
    self.schedule(r)
  File "/Users/anj/Documents/workspace/scrapy-url-frontier/venv/lib/python3.9/site-packages/frontera/strategy/__init__.py", line 122, in schedule
    self._scheduled_stream.send(request, score, dont_queue)
  File "/Users/anj/Documents/workspace/scrapy-url-frontier/venv/lib/python3.9/site-packages/frontera/core/manager.py", line 798, in send
    self._queue.schedule([(request.meta[b'fingerprint'], score, request, not dont_queue)])
AttributeError: 'NoneType' object has no attribute 'schedule'
```





## Notes on how the different parts work

URLFrontier implements crawl delay and deduplication, but not canonicalisation or any kind of filtering including robots.txt (see [here](https://github.com/crawler-commons/url-frontier/tree/master/API#out-of-scope)). The default crawl delay for each queue is one second (see [here](https://github.com/crawler-commons/url-frontier/blob/1b6c2ec4b14cff24810c718103eca16c8fa17d48/service/src/main/java/crawlercommons/urlfrontier/service/AbstractFrontierService.java#L118)).

Scrapy implements deduplication and canonicalisation via [request fingerprinting](https://docs.scrapy.org/en/latest/topics/request-response.html#request-fingerprints). It uses an internal [slot system to implement crawl delays](https://github.com/scrapy/scrapy/blob/master/scrapy/core/downloader/__init__.py#L140). And various kinds of filtering is supported, including [obeying robot.txt](https://docs.scrapy.org/en/latest/_modules/scrapy/downloadermiddlewares/robotstxt.html#RobotsTxtMiddleware) amd [OffsetMiddleware](https://docs.scrapy.org/en/latest/topics/spider-middleware.html#module-scrapy.spidermiddlewares.offsite) as part of the standard setup.

So, when integrating Scrapy with URLFrontier, how this works depends on the integration pattern. If we can't consistently route queues, then we could shift to relying on URLFrontier to manage crawl delays, but each Scrapy spider would have to fetch it's own copy of robots.txt. This could perhaps be alleviated by using some kind of shared cache, possibly even re-using the archived versions from the archiving proxy. But there may be other per-site state that is best cached locally, like cookies or browser sessions.

However, if can consistently route queues to the same Scrapy spider instances, then we can set the URLFrontier delay to e.g. 0 and let Scrapy handle delays and local caching  of things like robots.txt etc. While avoiding adding more components, the current URLFrontier offers a couple of possible ways to implement this.

One would be for each spider to regularly list all queues, and knowing that it is spider _x_ of _N_, allocate a subset of the queues to itself. It would then only run `GetURLs` for those queues.  This would be quite nice, but because we can't use partial queue matches, each queue would need a separate `GetURLs` call. So this scales poorly.

It would be possible to use the queues as the partitions instead. i.e. there are _N_ queues that each cover _1/N_ of the crawl, rather than a queue per host. This would scale, but make the URL Frontier itself less useful, as per-host operations would no longer be easy and each 'queue' would be very large.

A more scalable alternative is to pre-partition the crawl using separate crawl IDs. If the crawl is called `domain_scan` we can define _P_ partitions and create crawl IDs like `domain_scan_1`, `domain_scan_2`, `domain_scan_3` ... Each _x/N_ spider would then allocate itself to one or more crawl partitions, with the simplest arrangement being _P=N_ i.e. one crawl partition per spider.  This should work fine, but if the number of partitions/spiders needs to be changed, it may be necessary to drain and re-partition the frontier.

