# -*- coding: utf-8 -*-

from StringIO import StringIO
from address.cache import ExcludeWordCache
from address.services import ExcludeWordImporter
from test import BaseTestCase

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
    
class ExcludeWordTestCase(BaseTestCase):
    def prepareImporter(self, body):
        importer = ExcludeWordImporter()
    
        self.mocker.restore()
    
        response = self.mocker.mock()
        response.set_status(204)
        importer.response = response
        
        request = self.mocker.mock()
        request.body_file
        self.mocker.result(StringIO(body))
        importer.request = request   
        
        self.mocker.replay()
        
        return importer

class ExcludeWordPostTest(ExcludeWordTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)             
        self.prepareImporter(u'{"word":"南路"}').post()
        
    def testMatch(self):
        self.assertTrue(ExcludeWordCache.isStartWith(u"南路"))        
    

class ExcludeWordPutTest(ExcludeWordTestCase, ExcludeWordTest):
    excludeWords = u'{"words": ["路", "中路", "中路", "西路", "中街", "西街路口"]}'

    def setUp(self):
        BaseTestCase.setUp(self)             
        self.prepareImporter(self.excludeWords).put()   
        
    
class ExcludeWordCacheTest(BaseTestCase, ExcludeWordTest):
    excludeWords = [u"路", u"中路", u"中路", u"西路", u"中街", u"西街路口"]
    
    def setUp(self):
        BaseTestCase.setUp(self)
        for word in self.excludeWords:
            ExcludeWordCache.put(word)      
        