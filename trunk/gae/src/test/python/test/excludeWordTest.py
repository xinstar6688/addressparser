# -*- coding: utf-8 -*-

from address.cache import ExcludeWordCache
from address.services import ExcludeWordImporter
from test import BaseTestCase
from StringIO import StringIO

class ExcludeWordTest:
    def testEmptyReader(self):
        self.assertFalse(ExcludeWordCache.isStartWith(u""))

    def testPartMatch(self):
        self.assertFalse(ExcludeWordCache.isStartWith(u"中"))

    def testMatchInMiddle(self):
        self.assertFalse(ExcludeWordCache.isStartWith(u"上中路口"))

    def testNoOverlap(self):
        self.assertTrue(ExcludeWordCache.isStartWith(u"西路23号"))

    def testOverlap(self):
        self.assertTrue(ExcludeWordCache.isStartWith(u"中街"))

    def testLongest(self):
        self.assertTrue(ExcludeWordCache.isStartWith(u"西街路口"))
    

class ExcludeWordImporterTest(BaseTestCase, ExcludeWordTest):
    excludeWords = u'{"words": ["路", "中路", "中路", "西路", "中街", "西街路口"]}'

    def setUp(self):
        BaseTestCase.setUp(self)
        
        request = self.mocker.mock()
        request.body_file
        self.mocker.result(StringIO(self.excludeWords))
        self.mocker.replay()

        importer = ExcludeWordImporter()
        importer.request = request
        
        importer.post()
    
class ExcludeWordCacheTest(BaseTestCase, ExcludeWordTest):
    excludeWords = [u"路", u"中路", u"中路", u"西路", u"中街", u"西街路口"]
    
    def setUp(self):
        BaseTestCase.setUp(self)
        for word in self.excludeWords:
            ExcludeWordCache.put(word)      
        