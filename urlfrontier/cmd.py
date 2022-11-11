'''
Command-line interface for URLFrontier
'''

import os
import sys
import json
import logging
import argparse

import grpc
from urlfrontier.grpc.urlfrontier_pb2_grpc import URLFrontierStub
from urlfrontier.grpc.urlfrontier_pb2 import AnyCrawlID, GetParams, URLInfo, URLItem, DiscoveredURLItem, KnownURLItem, StringList, QueueWithinCrawlParams, Pagination, Local

logging.basicConfig(level=logging.WARNING, format='%(asctime)s: %(levelname)s - %(name)s - %(message)s')

logger = logging.getLogger(__name__)

def main():
    # Set up a parser:
    parser = argparse.ArgumentParser(prog='urlfrontier')

    # Common arguments:
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument('-v', '--verbose',  action='count', default=0, help='Logging level; add more -v for more logging.')
    common_parser.add_argument('-u', '--urlfrontier-endpoint', type=str, help='The URLFrontier instance to talk to.', required=True)

    queue_parser = argparse.ArgumentParser(add_help=False)
    queue_parser.add_argument('-C', '--crawl-id', default="DEFAULT", help="The CrawlID to use.")
    queue_parser.add_argument('-q', '--queue', required=True, help="Key for the crawl queue, e.g. 'example.com'.")

    # Use sub-parsers for different operations:
    subparsers = parser.add_subparsers(dest="op")
    subparsers.required = True

    # Add a parser a subcommand:
    parser_getstats = subparsers.add_parser(
        'get-stats', 
        help='Get stats from URLFrontier.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[common_parser])
    #parser_getstats.add_argument('id', type=str, help='The record ID to look up, or "-" to read a list of IDs from STDIN.')


    # Add a parser a subcommand:
    parser_listcrawlss = subparsers.add_parser(
        'list-crawls', 
        help='List crawls known to the URLFrontier.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[common_parser])

    # Add a parser a subcommand:
    parser_listqueues = subparsers.add_parser(
        'list-queues', 
        help='List queues known to the URLFrontier.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[common_parser])

    # Add a parser a subcommand:
    parser_delqueue = subparsers.add_parser(
        'delete-queue', 
        help='Delete a queue from the URLFrontier',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[common_parser, queue_parser])

    # Add a parser a subcommand:
    parser_listurls = subparsers.add_parser(
        'list-urls', 
        help='List URLs from the URLFrontier (with delay_requestable=0 so this does not interfere with the crawl).',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[common_parser])

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
                crawlID="",
                local=False
            )
            stats = stub.GetStats(q)
            print(stats)
        elif args.op == 'list-queues':
            p = Pagination(
                start = 0,
                size = 100,
                include_inactive = True,
                crawlID = b"",
                local = False
            )
            queues = stub.ListQueues(p)
            print(queues)
        elif args.op == 'list-crawls':
            crawls = stub.ListCrawls(Local(local=False))
            print(crawls)
        elif args.op == 'list-urls':
            g = GetParams(
                max_urls_per_queue = 100,
                max_queues = 0,
                delay_requestable = 1,
                #key = "example.com",
                #crawlID = "", # Needed if querying a specific queue key, otherwise:
                anyCrawlID = AnyCrawlID()
            )
            print(g)
            for uf_response in stub.GetURLs(g):
                logger.warn("GetURLs rx url=%s, metadata=%s" % (uf_response.url, uf_response.metadata))
        elif args.op == 'put-urls':
            raise Exception("Unimplemented operation " + args.op)
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
                local=False,
            )
            deleted = stub.DeleteQueue(d)
            print(f"Deleted {deleted.value} URLs from queue {queue} of crawl {crawlID}.")
        else:
            raise Exception("Unrecognized operation " + args.op)

if __name__ == "__main__":
    main()