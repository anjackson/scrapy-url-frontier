scrapy-url-frontier
===================

Just attempting to test integration with URL Frontier.

Steps Taken
-----------

Build and run the URL Frontier

    mvn install
    cd service
    java -cp target/urlfrontier-service-0.4-SNAPSHOT.jar crawlercommons.urlfrontier.service.URLFrontierServer

In another terminal...

Set up a virtualenv and installed all requirements (`scrapy`, `grpc` and `grpc-tools`).

Generated stubs with:

    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. urlfrontier.proto

Then ran a simple spider with:

    scrapy crawl example

The crawl runs at this point, and because `allowed_domains` is unset, quickly widens in scope to cover a number of hosts.

If the crawl it killed and restarted, the crawl will continue to get the URLs that were discovered but not crawled.

But the crawl will not make a full restart, i.e. the URL Frontier acts as a dupe filter. However, seed URLs get marked as `dont_filter` and this is implemented here as allowing immediate recrawl, so seeds will be re-fetched on restarts.

So, it basically works, but will require much more work to function properly.  This includes (at least):

- [x] Consider implementing as a [Frontera](https://frontera.readthedocs.io/) [back-end](https://frontera.readthedocs.io/en/latest/topics/frontier-backends.html) - this will handle a lot of the management logic around encoding properties, stats, etc. but is more complex to implement
- [x] Map any important properties and metadata from Scrapy's `Request` class to `URLInfo.metadata` and back again (see notes below).
- [x] Consider supporting `dont_filter` by enqueuing those URLs as `KnownURLItem` instances with the `refetchable_from_date` set appropriately. (n.b. "The default implementation [of start_requests()] generates Request(url, dont_filter=True) for each url in start_urls.")
- [ ] Decide how to handle URL canonicalization.
- [ ] Check `crawl-delay` works, i.e. is it handled in Scrapy, or do we need to be using `SetDelay` somehow?
- [ ] Setup the full via-WARC-writing-proxy Docker Stack.
- [ ] Consider schemes to partition queues across multiple instances of Scrapy. i.e. if a Scrapy knows it is Scrapy 1 of 10, then periodically list the queues and assign a stable subset to each Scrapy (e.g. hash the queue keys and distribute those - as we did for Kafka+H3).
- [ ] Consider making use of the URL Frontier support for additional stats.
- [ ] Add a Prometheus endpoint to the URL Frontier service.


Serialisation is an interesting issue. The `Request` can have references to Callable functions, and even to thread locks, so can't be pickled as-is.  We can follow Frontera's lead and [just keep these critical elements](https://github.com/scrapinghub/frontera/blob/84f9e1034d2868447db88e865596c0fbb32e70f6/frontera/contrib/backends/remote/codecs/json.py#L58-L63) (while noting that `dont_filter` is not included at present, may be missing `formdata` or `data` from form or JSON requests). But we must note that this will drop any callbacks attached to specific requests (the same as for Frontera, which [throws an error if you break this rule](https://github.com/scrapinghub/scrapy-frontera/blob/fab14232bedbe89b781479a13918eb3166a1564e/scrapy_frontera/scheduler.py#L29-L37)).

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