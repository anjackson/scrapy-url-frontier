'''
Command-line interface for URLFrontier
'''

import os
import sys
import json
import logging
import argparse

from scrapy.http.request import Request

import grpc
from urlfrontier.grpc.urlfrontier_pb2_grpc import URLFrontierStub
from urlfrontier.grpc.urlfrontier_pb2 import AnyCrawlID, GetParams, URLInfo, URLItem, DiscoveredURLItem, KnownURLItem, StringList, QueueWithinCrawlParams, Pagination, Local, DeleteCrawlMessage

from urlfrontier.scheduler import request_to_urlInfo, urlInfo_to_request
from urlfrontier.distribution import HashRingDistributor

logging.basicConfig(level=logging.WARNING, format='%(asctime)s: %(levelname)s - %(name)s - %(message)s')

logger = logging.getLogger(__name__)

# Fix the local parameter for calls here for the time being.
DEFAULT_LOCAL=False


def main():
    # Set up a parser:
    parser = argparse.ArgumentParser(prog='urlfrontier')

    # Common arguments:
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument('-v', '--verbose',  action='count', default=0, help='Logging level; add more -v for more logging.')
    common_parser.add_argument('-u', '--urlfrontier-endpoint', type=str, help='The URLFrontier instance to talk to.', default='localhost:7071')

    crawlid_parser = argparse.ArgumentParser(add_help=False)
    crawlid_parser.add_argument('-C', '--crawl-id', default=None, help="The CrawlID to use.")

    # Use sub-parsers for different operations:
    subparsers = parser.add_subparsers(dest="op")
    subparsers.required = True

    # Add a parser a subcommand:
    parser_getstats = subparsers.add_parser(
        'get-stats', 
        help='Get stats from URLFrontier.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[common_parser, crawlid_parser])
    #parser_getstats.add_argument('id', type=str, help='The record ID to look up, or "-" to read a list of IDs from STDIN.')


    # Add a parser a subcommand:
    parser_listcrawls = subparsers.add_parser(
        'list-crawls', 
        help='List crawls known to the URLFrontier.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[common_parser])

    # Add a parser a subcommand:
    parser_delcrawl = subparsers.add_parser(
        'delete-crawl', 
        help='Delete an entire crawl from the URLFrontier',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[common_parser, crawlid_parser])

    # Add a parser a subcommand:
    parser_listqueues = subparsers.add_parser(
        'list-queues', 
        help='List queues known to the URLFrontier.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[common_parser,crawlid_parser])

    # Add a parser a subcommand:
    parser_delqueue = subparsers.add_parser(
        'delete-queue', 
        help='Delete a queue from the URLFrontier',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[common_parser, crawlid_parser])
    parser_delqueue.add_argument('queue', help="Key for the crawl queue to delete, e.g. 'example.com'.")

    # Add a parser a subcommand:
    parser_listurls = subparsers.add_parser(
        'list-urls', 
        help='List URLs from the URLFrontier (with delay_requestable=0 so this does not interfere with the crawl).',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[common_parser, crawlid_parser])
    parser_listurls.add_argument('-q', '--queue', help="Key for the crawl queue to list URLs from, e.g. 'example.com'.")

    # Add a parser a subcommand:
    parser_puturls = subparsers.add_parser(
        'put-urls', 
        help='Put URLs into the URLFrontier.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[common_parser, crawlid_parser])
    parser_puturls.add_argument('-q', '--queue', help="Key for the crawl queue to add the URL(s) to. If unset, uses the host name.")
    parser_puturls.add_argument('-N', '--num-partitions', type=int, default=None, help="Number of partitions to use. If set, Crawl ID (spider name) has a partition suffix added, eg. 'crawl.2'.")
    parser_puturls.add_argument('--partition-separator', default=".", help="Character to use to separate the Crawl ID (spider name) from the partition number.")
    parser_puturls.add_argument('urls', help="URL to enqueue, or a filename to read URLs from, or '-' to read from STDIN.")


    # And PARSE it:
    args = parser.parse_args()

    # Set up verbose logging:
    if args.verbose == 1:
        logging.getLogger().setLevel(logging.INFO)
    elif args.verbose >= 2:
        logging.getLogger().setLevel(logging.DEBUG)

    # Set up URL Frontier connection:
    with grpc.insecure_channel(args.urlfrontier_endpoint) as channel:
        # Setup service interface
        stub = URLFrontierStub(channel)

        # Ops:
        logger.debug("Got args: %s" % args)
        if args.op == 'get-stats':
            q = QueueWithinCrawlParams(
                key="",
                crawlID=args.crawl_id,
                local=DEFAULT_LOCAL
            )
            stats = stub.GetStats(q)
            print(stats)
        elif args.op == 'list-queues':
            p = Pagination(
                start = 0,
                size = 100,
                include_inactive = True,
                crawlID = args.crawl_id,
                local = DEFAULT_LOCAL
            )
            queues = stub.ListQueues(p)
            print(queues)
        elif args.op == 'list-crawls':
            crawls = stub.ListCrawls(Local(local=DEFAULT_LOCAL))
            print(crawls)
        elif args.op == 'delete-crawl':
            deleted = stub.DeleteCrawl(
                    DeleteCrawlMessage(
                        value=args.crawl_id,
                        local=DEFAULT_LOCAL,
                    )
                )
            print(f"Deleted {deleted.value} URLs from crawl {args.crawl_id}.")
        elif args.op == 'list-urls':
            g = GetParams(
                max_urls_per_queue = 100,
                max_queues = 0,
                delay_requestable = 1,
                key = args.queue,
                crawlID = args.crawl_id, # Needed if querying a specific queue key, otherwise:
                #anyCrawlID = AnyCrawlID()
            )
            for uf_response in stub.GetURLs(g):
                print("url=%s, metadata=%s" % (uf_response.url, uf_response.metadata))
                request = urlInfo_to_request(uf_response)
                print(request)
        elif args.op == 'put-urls':
            # FIXME Need to support crawl distribution over crawl IDs
            if args.num_partitions is None:
                spider_id = None
                num_partitions = 1
            else:
                spider_id = 1 # Any value, to enable partitions
                num_partitions = args.num_partitions
            hr = HashRingDistributor(
                spider_id=spider_id,
                spider_name=args.crawl_id,
                num_spiders=num_partitions,
                separator=args.partition_separator,
            )
            request = Request(args.urls)
            request = hr.set_spider_id(request)
            urlInfo = request_to_urlInfo(request, 
                encoder=None)
            logger.info(f"URLInfo {urlInfo} with CrawlID {urlInfo.crawlID}")
            #uf_request = URLItem(known=KnownURLItem(info=urlInfo, refetchable_from_date=0))
            uf_request = URLItem(discovered=DiscoveredURLItem(info=urlInfo))
            for uf_response in stub.PutURLs(iter([uf_request])):
                # Status 0 OK, 1 Skipped, 2 FAILED
                logger.debug("PutURL ID=%s Status=%i" % (uf_response.ID, uf_response.status))

        elif args.op == 'get-active':
            raise Exception("Unimplemented operation " + args.op)

        elif args.op == 'set-active':
            raise Exception("Unimplemented operation " + args.op)

        elif args.op == 'delete-queue':
            queue = args.queue
            crawlID = args.crawl_id
            d = QueueWithinCrawlParams(
                key = queue,
                crawlID = crawlID,
                local=DEFAULT_LOCAL,
            )
            deleted = stub.DeleteQueue(d)
            print(f"Deleted {deleted.value} URLs from queue {queue} of crawl {crawlID}.")
        else:
            raise Exception("Unrecognized operation " + args.op)

if __name__ == "__main__":
    main()