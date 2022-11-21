scrapy-url-frontier
===================

This project provides a [Scheduler](https://docs.scrapy.org/en/latest/topics/scheduler.html) for [Scrapy](https://scrapy.org) that uses [crawler-commons URL Frontier](https://github.com/crawler-commons/url-frontier#readme). This can use used as a persistent frontier for multiple different spiders, and can be used to partition large crawls across multiple instances of the same spider.

This is an early experiment, and has not yet been used at scale or benchmarked. More mature options include:

- [Manual partitioning of large sets of URLs](https://docs.scrapy.org/en/latest/topics/practices.html#distributed-crawls)
- [Frontera](https://frontera.readthedocs.io/)
- [Scrapy Cluster](https://scrapy-cluster.readthedocs.io/)
- [Scrapy Cluster's list of other distributed Scrapy projects](https://scrapy-cluster.readthedocs.io/en/latest/topics/advanced/comparison.html)


## Usage

First, deploy an instance of a URL Frontier service. This module has been tested against the [reference implementation](https://github.com/crawler-commons/url-frontier/blob/master/service/README.md), and is known to be compatible with version 2.3.1.

A `docker-compose.yml` file is included, which can fire up a suitable service like this:

    docker compose up urlfrontier

To run a Scrapy spider that uses the URL Frontier, first install this module in your Scrapy project (or use the example crawler in this repository). There is no official release at present, so needs to be installed like this:

    pip install git+https://github.com/anjackson/scrapy-url-frontier.git@main

Once installed, the `Scheduler` can be configure like this:

    SCHEDULER='urlfrontier.scheduler.URLFrontierScheduler'
    SCHEDULER_URLFRONTIER_ENDPOINT='127.0.0.1:7071'

Scrapy schedulers implement deduplication and canonicalisation as per [request fingerprinting](https://docs.scrapy.org/en/latest/topics/request-response.html#request-fingerprints). The scheduler does not implement crawl rate control, but rather the Downloader uses an internal [slot system to implement crawl delays](https://github.com/scrapy/scrapy/blob/master/scrapy/core/downloader/__init__.py#L140). Scrapy also support various kinds of filtering, including [obeying robot.txt](https://docs.scrapy.org/en/latest/_modules/scrapy/downloadermiddlewares/robotstxt.html#RobotsTxtMiddleware) and [OffsetMiddleware](https://docs.scrapy.org/en/latest/topics/spider-middleware.html#module-scrapy.spidermiddlewares.offsite) as part of the standard setup.

FIXME? Talk more about Canonicalisation?

URLFrontier can be used to implement crawl rate/delay and deduplication, but not canonicalisation or any kind of filtering including robots.txt (see [here](https://github.com/crawler-commons/url-frontier/tree/master/API#out-of-scope)). The default crawl delay for each queue is one second (see [here](https://github.com/crawler-commons/url-frontier/blob/1b6c2ec4b14cff24810c718103eca16c8fa17d48/service/src/main/java/crawlercommons/urlfrontier/service/AbstractFrontierService.java#L118)). However, because Scrapy handles crawl delays in the Downloader rather than the Scheduler, the URL Frontier crawl delay becomes a kind of maximum speed. i.e. while URL Frontier emits one URL per second per queue, Scrapy may crawl more slowly depending on the configuration.

## Example Spider

In this project, the example spider can be run with with:

    scrapy crawl example

At this point, nothing will happen as there are no `start_urls` or `start_requests` set for the spider. To get things going, you can launch a URL into the crawl using the command-line tool:

    scrapy-url-frontier put-urls -u localhost:7071 -C example https://example.org/

Where the `-C example` sets the Crawl ID to match the name of the Scrapy spider. 

The crawl will now run, and because `allowed_domains` is unset, quickly widens in scope to cover a number of hosts.

If the crawl is killed and restarted, the crawl will continue to get the URLs that were discovered but not crawled.

But the crawl will not make a full restart, i.e. the URL Frontier acts as a duplicate filter. However, if URLs are marked as `dont_filter`, this is implemented here as allowing immediate re-crawl. i.e. a Scrapy request with `request.meta['dont_filter'] = True'.

If your spider sets `start_urls` or `start_requests`, these will be sent to the URL Frontier be every spider.  In general, this works fine as duplicate requests get filtered out. But if you also set 'dont_filter' this will make the seed URLs recrawl if one spider starts after another spider has already finished crawling those URLs.

## URL Frontier Command-Line Client

The `scrapy-url-frontier` client supports all URL Frontier operations (as of v. 2.3.1). for example:

    scrapy-url-frontier list-crawls -u localhost:7071

Will return a list of all Crawl IDs, corresponding to Scrapy spider names or name+partition in the case of distributed crawls (see below).

For each crawl, you can list URLs using e.g.

    scrapy-url-frontier list-urls -u localhost:7071 -C example

The full list of commands is:  `get-stats,list-crawls,delete-crawl,list-queues,delete-queue,list-urls,put-urls,get-active,set-active`. For more information, see the command line help e.g. `scrapy-url-frontier -h` or `scrapy-url-frontier list-queues -h`. 

## Distributed Crawls

The URL Frontier can also be used to distributed a crawl over multiple instances of the same Scrapy spider, allowing crawls to be scaled out beyond the capacity of a single crawler process.

To ensure resources like `robots.txt` are cached effectively, we partition the crawl queues so the same queues always get routed to the same spiders. For each unique spider, e.g. the `example` spider, we create different Crawl IDs for each partition. e.g. `example.1` and `example.2` for a crawl distributed over two spider instances.

Extending [Frontera's naming conventions](https://frontera.readthedocs.io/en/latest/topics/cluster-setup.html#starting-the-cluster) we can use [command-line options](https://docs.scrapy.org/en/latest/topics/settings.html#command-line-options) to configure the URL partitioning scheme:

    scrapy crawl example -s SPIDER_PARTITION_ID=1/2

And elsewhere:

    scrapy crawl example -s SPIDER_PARTITION_ID=2/2

The `put-urls` command also needs to be aware of the number of partitions so it re-uses the right Crawl IDs and routes the URLs to the right place:

    scrapy-url-frontier put-urls -u localhost:7071 -C example -N 2 https://example.org/

The system uses a consistent hashing method to distribute the URLs. This minimizes the disruption if the number of partitions changes, e.g. if a `N=4` crawl is stopped and restarted with `N=5`, only one fifth of the URLs will be affected. However, during the period while the URLs are being drained out of the `N=4` scheme, new URLs for the same hosts will arrive in the fifth partition and so those affected sites will be crawled at a higher rate. This issue is noted [here](https://github.com/anjackson/scrapy-url-frontier/issues/3).

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



