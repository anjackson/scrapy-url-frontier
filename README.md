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

- [ ] Map any important properties and metadata from Scrapy's `Request` class to `URLInfo.metadata` and back again (see notes below).
- [ ] Decide how to handle URL canonicalization.
- [x] Consider supporting `dont_filter` by enqueuing those URLs as `KnownURLItem` instances with the `refetchable_from_date` set appropriately. (n.b. "The default implementation [of start_requests()] generates Request(url, dont_filter=True) for each url in start_urls.")
- [ ] Setup the full via-WARC-writing-proxy Docker Stack.
- [ ] Check `crawl-delay` works, i.e. is it handled in Scrapy, or do we need to be using `SetDelay` somehow?
- [ ] Consider schemes to partition queues across multiple instances of Scrapy. i.e. if a Scrapy knows it is Scrapy 1 of 10, then periodically list the queues and assign a stable subset to each Scrapy (e.g. hash the queue keys and distribute those - as we did for Kafka+H3).
- [ ] Consider making use of the URL Frontier support for additional stats.
- [ ] Add a Prometheus endpoint to the URL Frontier service.


Serialisation is an interesting issue. The `Request` can have hooks to Callable functions, and even to thread locks, so can't be pickled as-is.  We can follow Frontera's lead and [just keep the critical elements](https://github.com/scrapinghub/frontera/blob/84f9e1034d2868447db88e865596c0fbb32e70f6/frontera/contrib/backends/remote/codecs/json.py#L58-L63) (while noting that `dont_filter` is not included at present, may be missing `formdata` or `data` from form or JSON requests). But we must note that this will drop any callbacks attached to specific requests (the same as for Frontera, so presumable this is fine).