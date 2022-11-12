import unittest

from scrapy.http.request import Request
from scrapy.http.response import Response

from urlfrontier.grpc.urlfrontier_pb2 import GetParams, URLInfo, URLItem, DiscoveredURLItem, KnownURLItem, StringList


from urlfrontier.scheduler import request_to_urlInfo, urlInfo_to_request

class TestUrlInfoCodec(unittest.TestCase):

    def test_codec(self):
        req = Request(url="https://www.example.com/")
        print(req)
        uf = request_to_urlInfo(req)
        print(uf)
        req2 = urlInfo_to_request(uf)
        print(req2)


class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()
