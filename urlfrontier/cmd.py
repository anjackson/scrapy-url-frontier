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
from urlfrontier.grpc.urlfrontier_pb2 import AnyCrawlID, GetParams, URLInfo, URLItem, DiscoveredURLItem, KnownURLItem, StringList, QueueWithinCrawlParams, Pagination, Local, DeleteCrawlMessage

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
    common_parser.add_argument('-u', '--urlfrontier-endpoint', type=str, help='The URLFrontier instance to talk to.', required=True)

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
                #key = "example.com",
                crawlID = args.crawl_id, # Needed if querying a specific queue key, otherwise:
                #anyCrawlID = AnyCrawlID()
            )
            for uf_response in stub.GetURLs(g):
                print("url=%s, metadata=%s" % (uf_response.url, uf_response.metadata))
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
                local=DEFAULT_LOCAL,
            )
            deleted = stub.DeleteQueue(d)
            print(f"Deleted {deleted.value} URLs from queue {queue} of crawl {crawlID}.")
        else:
            raise Exception("Unrecognized operation " + args.op)

if __name__ == "__main__":
    main()