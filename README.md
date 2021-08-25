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

The crawler attempts to enqueue the start URL, but the URL Frontier is unhappy:

```
SEVERE: Exception while executing runnable io.grpc.internal.ServerImpl$JumpToApplicationThreadServerStreamListener$1MessagesAvailable@352d3e9
io.grpc.StatusRuntimeException: INTERNAL: Invalid protobuf byte sequence
	at io.grpc.Status.asRuntimeException(Status.java:526)
	at io.grpc.protobuf.lite.ProtoLiteUtils$MessageMarshaller.parse(ProtoLiteUtils.java:218)
	at io.grpc.protobuf.lite.ProtoLiteUtils$MessageMarshaller.parse(ProtoLiteUtils.java:118)
	at io.grpc.MethodDescriptor.parseRequest(MethodDescriptor.java:307)
	at io.grpc.internal.ServerCallImpl$ServerStreamListenerImpl.messagesAvailableInternal(ServerCallImpl.java:309)
	at io.grpc.internal.ServerCallImpl$ServerStreamListenerImpl.messagesAvailable(ServerCallImpl.java:292)
	at io.grpc.internal.ServerImpl$JumpToApplicationThreadServerStreamListener$1MessagesAvailable.runInContext(ServerImpl.java:765)
	at io.grpc.internal.ContextRunnable.run(ContextRunnable.java:37)
	at io.grpc.internal.SerializingExecutor.run(SerializingExecutor.java:123)
	at java.base/java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1128)
	at java.base/java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:628)
	at java.base/java.lang.Thread.run(Thread.java:829)
Caused by: com.google.protobuf.InvalidProtocolBufferException: Protocol message end-group tag did not match expected tag.
	at com.google.protobuf.InvalidProtocolBufferException.invalidEndTag(InvalidProtocolBufferException.java:129)
	at com.google.protobuf.CodedInputStream$ArrayDecoder.checkLastTagWas(CodedInputStream.java:636)
	at com.google.protobuf.CodedInputStream$ArrayDecoder.readMessage(CodedInputStream.java:890)
	at crawlercommons.urlfrontier.Urlfrontier$DiscoveredURLItem.<init>(Urlfrontier.java:10474)
	at crawlercommons.urlfrontier.Urlfrontier$DiscoveredURLItem.<init>(Urlfrontier.java:10427)
	at crawlercommons.urlfrontier.Urlfrontier$DiscoveredURLItem$1.parsePartialFrom(Urlfrontier.java:11011)
	at crawlercommons.urlfrontier.Urlfrontier$DiscoveredURLItem$1.parsePartialFrom(Urlfrontier.java:11005)
	at com.google.protobuf.CodedInputStream$ArrayDecoder.readMessage(CodedInputStream.java:889)
	at crawlercommons.urlfrontier.Urlfrontier$URLItem.<init>(Urlfrontier.java:7601)
	at crawlercommons.urlfrontier.Urlfrontier$URLItem.<init>(Urlfrontier.java:7553)
	at crawlercommons.urlfrontier.Urlfrontier$URLItem$1.parsePartialFrom(Urlfrontier.java:8445)
	at crawlercommons.urlfrontier.Urlfrontier$URLItem$1.parsePartialFrom(Urlfrontier.java:8439)
	at com.google.protobuf.AbstractParser.parseFrom(AbstractParser.java:86)
	at com.google.protobuf.AbstractParser.parseFrom(AbstractParser.java:48)
	at io.grpc.protobuf.lite.ProtoLiteUtils$MessageMarshaller.parseFrom(ProtoLiteUtils.java:223)
	at io.grpc.protobuf.lite.ProtoLiteUtils$MessageMarshaller.parse(ProtoLiteUtils.java:215)
	... 10 more
```


