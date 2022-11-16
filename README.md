scrapy-url-frontier
===================

This project provides a [Scheduler](https://docs.scrapy.org/en/latest/topics/scheduler.html) for [Scrapy](https://scrapy.org) that uses [crawler-commons URL Frontier](https://github.com/crawler-commons/url-frontier#readme). This can use used as a persistent frontier for multiple different spiders, and can be used to partition broad crawls across multiple instances of the same spider.

This is an early experiment, and has not yet been used at scale or benchmarked. More mature options include:

- [Manual partitioning of large sets of URLs](https://docs.scrapy.org/en/latest/topics/practices.html#distributed-crawls)
- [Frontera](https://frontera.readthedocs.io/)
- [Scrapy Cluster](https://scrapy-cluster.readthedocs.io/)
- [Scrapy Cluster's list of other distributed Scrapy projects](https://scrapy-cluster.readthedocs.io/en/latest/topics/advanced/comparison.html)


## Usage

First, deploy an instance of a URL Frontier service. This module has been tested against the [reference implementation](https://github.com/crawler-commons/url-frontier/blob/master/service/README.md), and is known to be compatible with version 2.4.

A `docker-compose.yml` file is included, which can fire up a suitable service like this:

    docker compose up urlfrontier

To run a Scrapy spider that uses the URL Frontier, the Scheduler can be configure like this:

    SCHEDULER='urlfrontier.scheduler.URLFrontierScheduler'
    SCHEDULER_URLFRONTIER_ENDPOINT='127.0.0.1:7071'

Scrapy schedulers implement deduplication and canonicalisation as per [request fingerprinting](https://docs.scrapy.org/en/latest/topics/request-response.html#request-fingerprints). The scheduler does not implement crawl rate control, but rather the Downloader uses an internal [slot system to implement crawl delays](https://github.com/scrapy/scrapy/blob/master/scrapy/core/downloader/__init__.py#L140). Scrapy also support various kinds of filtering, including [obeying robot.txt](https://docs.scrapy.org/en/latest/_modules/scrapy/downloadermiddlewares/robotstxt.html#RobotsTxtMiddleware) and [OffsetMiddleware](https://docs.scrapy.org/en/latest/topics/spider-middleware.html#module-scrapy.spidermiddlewares.offsite) as part of the standard setup.

FIXME? Talk more about Canonicalisation?

URLFrontier can be used to implement crawl rate/delay and deduplication, but not canonicalisation or any kind of filtering including robots.txt (see [here](https://github.com/crawler-commons/url-frontier/tree/master/API#out-of-scope)). The default crawl delay for each queue is one second (see [here](https://github.com/crawler-commons/url-frontier/blob/1b6c2ec4b14cff24810c718103eca16c8fa17d48/service/src/main/java/crawlercommons/urlfrontier/service/AbstractFrontierService.java#L118)). However, because Scrapy handles crawl delays in the Downloader rather than the Scheduler, the URL Frontier crawl delay becomes a kind of maximum speed. i.e. while URL Frontier emits one URL per second per queue, Scrapy may crawl more slowly depending on the configuration.

## Example Spider

Then ran a simple spider with:

    scrapy crawl example

The crawl runs at this point, and because `allowed_domains` is unset, quickly widens in scope to cover a number of hosts.

If the crawl is killed and restarted, the crawl will continue to get the URLs that were discovered but not crawled.

But the crawl will not make a full restart, i.e. the URL Frontier acts as a dupe filter. However, seed URLs get marked as `dont_filter` and this is implemented here as allowing immediate recrawl, so seeds will be re-fetched on restarts.

## URL Frontier Client

    scrapy-url-frontier list-crawls -u localhost:7071


## Distributed Crawls


So, when integrating Scrapy with URLFrontier, how this works depends on the integration pattern. If we can't consistently route queues, then we could shift to relying on URLFrontier to manage crawl delays, but each Scrapy spider would have to fetch it's own copy of robots.txt. This could perhaps be alleviated by using some kind of shared cache, possibly even re-using the archived versions from the archiving proxy. But there may be other per-site state that is best cached locally, like cookies or browser sessions.

However, if can consistently route queues to the same Scrapy spider instances, then we can set the URLFrontier delay to e.g. 0 and let Scrapy handle delays and local caching  of things like robots.txt etc. While avoiding adding more components, the current URLFrontier offers a couple of possible ways to implement this.

One would be for each spider to regularly list all queues, and knowing that it is spider _x_ of _N_, allocate a subset of the queues to itself. It would then only run `GetURLs` for those queues.  This would be quite nice, but because we can't use partial queue matches, each queue would need a separate `GetURLs` call. So this scales poorly.

It would be possible to use the queues as the partitions instead. i.e. there are _N_ queues that each cover _1/N_ of the crawl, rather than a queue per host. This would scale, but make the URL Frontier itself less useful, as per-host operations would no longer be easy and each 'queue' would be very large.

A more scalable alternative is to pre-partition the crawl using separate crawl IDs. If the crawl is called `domain_scan` we can define _P_ partitions and create crawl IDs like `domain_scan_1`, `domain_scan_2`, `domain_scan_3` ... Each _x/N_ spider would then allocate itself to one or more crawl partitions, with the simplest arrangement being _P=N_ i.e. one crawl partition per spider.  This should work fine, but if the number of partitions/spiders needs to be changed, it may be necessary to drain and re-partition the frontier.


Extending [Frontera's naming conventions](https://frontera.readthedocs.io/en/latest/topics/cluster-setup.html#starting-the-cluster) we can use [command-line options](https://docs.scrapy.org/en/latest/topics/settings.html#command-line-options) to configure the URL partitioning scheme:

    scrapy crawl example -s SPIDER_PARTITION_ID=1/2


## Alternative Encoders

    SCHEDULER_URLFRONTIER_CODEC='frontera.contrib.backends.remote.codecs.json'


Serialisation is an interesting issue. The `Request` can have references to Callable functions, and even to thread locks, so can't necessarily be pickled as-is.  We can follow Frontera's lead and [just keep these critical elements](https://github.com/scrapinghub/frontera/blob/84f9e1034d2868447db88e865596c0fbb32e70f6/frontera/contrib/backends/remote/codecs/json.py#L58-L63) (while noting that `dont_filter` is not included at present, may be missing `formdata` or `data` from form or JSON requests). But we must note that this will drop any callbacks attached to specific requests (the same as for Frontera, which [throws an error if you break this rule](https://github.com/scrapinghub/scrapy-frontera/blob/fab14232bedbe89b781479a13918eb3166a1564e/scrapy_frontera/scheduler.py#L29-L37)).




## Development Setup

Build and run the URL Frontier, as per the instructions. Or, use the supplied Docker Compose file:

    docker compose up urlfrontier

Alternative to build...

    docker build -t crawlercommons/url-frontier:master .

In another terminal...

    sudo apt-get install libffi-dev

Set up a virtualenv and installed all requirements (`scrapy`, `scrapy-playwright`, `grpc` and `grpc-tools`).

Generated stubs with:

    curl -o urlfrontier/grpc/urlfrontier.proto https://raw.githubusercontent.com/crawler-commons/url-frontier/2.3/API/urlfrontier.proto
    python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. urlfrontier/grpc/urlfrontier.proto



