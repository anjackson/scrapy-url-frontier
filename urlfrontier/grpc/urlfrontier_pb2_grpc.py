# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from urlfrontier.grpc import urlfrontier_pb2 as urlfrontier_dot_grpc_dot_urlfrontier__pb2


class URLFrontierStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ListNodes = channel.unary_unary(
                '/urlfrontier.URLFrontier/ListNodes',
                request_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Empty.SerializeToString,
                response_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.StringList.FromString,
                )
        self.ListCrawls = channel.unary_unary(
                '/urlfrontier.URLFrontier/ListCrawls',
                request_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Local.SerializeToString,
                response_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.StringList.FromString,
                )
        self.DeleteCrawl = channel.unary_unary(
                '/urlfrontier.URLFrontier/DeleteCrawl',
                request_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.DeleteCrawlMessage.SerializeToString,
                response_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Long.FromString,
                )
        self.ListQueues = channel.unary_unary(
                '/urlfrontier.URLFrontier/ListQueues',
                request_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Pagination.SerializeToString,
                response_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.QueueList.FromString,
                )
        self.GetURLs = channel.unary_stream(
                '/urlfrontier.URLFrontier/GetURLs',
                request_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.GetParams.SerializeToString,
                response_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.URLInfo.FromString,
                )
        self.PutURLs = channel.stream_stream(
                '/urlfrontier.URLFrontier/PutURLs',
                request_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.URLItem.SerializeToString,
                response_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.AckMessage.FromString,
                )
        self.GetStats = channel.unary_unary(
                '/urlfrontier.URLFrontier/GetStats',
                request_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.QueueWithinCrawlParams.SerializeToString,
                response_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Stats.FromString,
                )
        self.DeleteQueue = channel.unary_unary(
                '/urlfrontier.URLFrontier/DeleteQueue',
                request_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.QueueWithinCrawlParams.SerializeToString,
                response_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Long.FromString,
                )
        self.BlockQueueUntil = channel.unary_unary(
                '/urlfrontier.URLFrontier/BlockQueueUntil',
                request_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.BlockQueueParams.SerializeToString,
                response_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Empty.FromString,
                )
        self.SetActive = channel.unary_unary(
                '/urlfrontier.URLFrontier/SetActive',
                request_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Active.SerializeToString,
                response_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Empty.FromString,
                )
        self.GetActive = channel.unary_unary(
                '/urlfrontier.URLFrontier/GetActive',
                request_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Local.SerializeToString,
                response_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Boolean.FromString,
                )
        self.SetDelay = channel.unary_unary(
                '/urlfrontier.URLFrontier/SetDelay',
                request_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.QueueDelayParams.SerializeToString,
                response_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Empty.FromString,
                )
        self.SetLogLevel = channel.unary_unary(
                '/urlfrontier.URLFrontier/SetLogLevel',
                request_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.LogLevelParams.SerializeToString,
                response_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Empty.FromString,
                )


class URLFrontierServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ListNodes(self, request, context):
        """* Return the list of nodes forming the cluster the current node belongs to *
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListCrawls(self, request, context):
        """* Return the list of crawls handled by the frontier(s) *
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteCrawl(self, request, context):
        """* Delete an entire crawl, returns the number of URLs removed this way *
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListQueues(self, request, context):
        """* Return a list of queues for a specific crawl. Can chose whether to include inactive queues (a queue is active if it has URLs due for fetching);
        by default the service will return up to 100 results from offset 0 and exclude inactive queues.*
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetURLs(self, request, context):
        """* Stream URLs due for fetching from M queues with up to N items per queue *
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def PutURLs(self, request_iterator, context):
        """* Push URL items to the server; they get created (if they don't already exist) in case of DiscoveredURLItems or updated if KnownURLItems *
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetStats(self, request, context):
        """* Return stats for a specific queue or an entire crawl. Does not aggregate the stats across different crawlids. *
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteQueue(self, request, context):
        """* Delete the queue based on the key in parameter, returns the number of URLs removed this way *
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def BlockQueueUntil(self, request, context):
        """* Block a queue from sending URLs; the argument is the number of seconds of UTC time since Unix epoch
        1970-01-01T00:00:00Z. The default value of 0 will unblock the queue. The block will get removed once the time
        indicated in argument is reached. This is useful for cases where a server returns a Retry-After for instance. 
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetActive(self, request, context):
        """* De/activate the crawl. GetURLs will not return anything until SetActive is set to true. PutURLs will still take incoming data. *
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetActive(self, request, context):
        """* Returns true if the crawl is active, false if it has been deactivated with SetActive(Boolean) *
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetDelay(self, request, context):
        """* Set a delay from a given queue.
        No URLs will be obtained via GetURLs for this queue until the number of seconds specified has 
        elapsed since the last time URLs were retrieved.
        Usually informed by the delay setting of robots.txt.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetLogLevel(self, request, context):
        """* Overrides the log level for a given package *
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_URLFrontierServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ListNodes': grpc.unary_unary_rpc_method_handler(
                    servicer.ListNodes,
                    request_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Empty.FromString,
                    response_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.StringList.SerializeToString,
            ),
            'ListCrawls': grpc.unary_unary_rpc_method_handler(
                    servicer.ListCrawls,
                    request_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Local.FromString,
                    response_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.StringList.SerializeToString,
            ),
            'DeleteCrawl': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteCrawl,
                    request_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.DeleteCrawlMessage.FromString,
                    response_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Long.SerializeToString,
            ),
            'ListQueues': grpc.unary_unary_rpc_method_handler(
                    servicer.ListQueues,
                    request_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Pagination.FromString,
                    response_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.QueueList.SerializeToString,
            ),
            'GetURLs': grpc.unary_stream_rpc_method_handler(
                    servicer.GetURLs,
                    request_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.GetParams.FromString,
                    response_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.URLInfo.SerializeToString,
            ),
            'PutURLs': grpc.stream_stream_rpc_method_handler(
                    servicer.PutURLs,
                    request_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.URLItem.FromString,
                    response_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.AckMessage.SerializeToString,
            ),
            'GetStats': grpc.unary_unary_rpc_method_handler(
                    servicer.GetStats,
                    request_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.QueueWithinCrawlParams.FromString,
                    response_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Stats.SerializeToString,
            ),
            'DeleteQueue': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteQueue,
                    request_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.QueueWithinCrawlParams.FromString,
                    response_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Long.SerializeToString,
            ),
            'BlockQueueUntil': grpc.unary_unary_rpc_method_handler(
                    servicer.BlockQueueUntil,
                    request_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.BlockQueueParams.FromString,
                    response_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Empty.SerializeToString,
            ),
            'SetActive': grpc.unary_unary_rpc_method_handler(
                    servicer.SetActive,
                    request_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Active.FromString,
                    response_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Empty.SerializeToString,
            ),
            'GetActive': grpc.unary_unary_rpc_method_handler(
                    servicer.GetActive,
                    request_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Local.FromString,
                    response_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Boolean.SerializeToString,
            ),
            'SetDelay': grpc.unary_unary_rpc_method_handler(
                    servicer.SetDelay,
                    request_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.QueueDelayParams.FromString,
                    response_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Empty.SerializeToString,
            ),
            'SetLogLevel': grpc.unary_unary_rpc_method_handler(
                    servicer.SetLogLevel,
                    request_deserializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.LogLevelParams.FromString,
                    response_serializer=urlfrontier_dot_grpc_dot_urlfrontier__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'urlfrontier.URLFrontier', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class URLFrontier(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ListNodes(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/urlfrontier.URLFrontier/ListNodes',
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.Empty.SerializeToString,
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.StringList.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ListCrawls(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/urlfrontier.URLFrontier/ListCrawls',
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.Local.SerializeToString,
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.StringList.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DeleteCrawl(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/urlfrontier.URLFrontier/DeleteCrawl',
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.DeleteCrawlMessage.SerializeToString,
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.Long.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ListQueues(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/urlfrontier.URLFrontier/ListQueues',
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.Pagination.SerializeToString,
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.QueueList.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetURLs(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/urlfrontier.URLFrontier/GetURLs',
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.GetParams.SerializeToString,
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.URLInfo.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def PutURLs(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(request_iterator, target, '/urlfrontier.URLFrontier/PutURLs',
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.URLItem.SerializeToString,
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.AckMessage.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetStats(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/urlfrontier.URLFrontier/GetStats',
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.QueueWithinCrawlParams.SerializeToString,
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.Stats.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DeleteQueue(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/urlfrontier.URLFrontier/DeleteQueue',
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.QueueWithinCrawlParams.SerializeToString,
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.Long.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def BlockQueueUntil(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/urlfrontier.URLFrontier/BlockQueueUntil',
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.BlockQueueParams.SerializeToString,
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SetActive(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/urlfrontier.URLFrontier/SetActive',
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.Active.SerializeToString,
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetActive(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/urlfrontier.URLFrontier/GetActive',
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.Local.SerializeToString,
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.Boolean.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SetDelay(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/urlfrontier.URLFrontier/SetDelay',
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.QueueDelayParams.SerializeToString,
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SetLogLevel(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/urlfrontier.URLFrontier/SetLogLevel',
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.LogLevelParams.SerializeToString,
            urlfrontier_dot_grpc_dot_urlfrontier__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
