# -*- coding: utf-8 -*-

from StringIO import StringIO
from address.caches import ExcludeWordCharCache
from address.services import ExcludeWordsService
from test import BaseTestCase, excludeWords

class ExcludeWordTest:
    def testEmptyReader(self):
        self.assertFalse(ExcludeWordCharCache.isStartWith(u""))

    def testPartMatch(self):
        self.assertFalse(ExcludeWordCharCache.isStartWith(u"中"))

    def testMatchInMiddle(self):
        self.assertFalse(ExcludeWordCharCache.isStartWith(u"上中路口"))

    def testNoOverlap(self):
        self.assertTrue(ExcludeWordCharCache.isStartWith(u"西路23号"))

    def testOverlap(self):
        self.assertTrue(ExcludeWordCharCache.isStartWith(u"中街"))

    def testLongest(self):
        self.assertTrue(ExcludeWordCharCache.isStartWith(u"西街路口"))
    
class ExcludeWordsServiceTest(BaseTestCase):
    def prepareService(self, body):
        service = ExcludeWordsService()
    
        self.mocker.restore()
    
        response = self.mocker.mock()
        response.set_status(204)
        service.response = response
        
        request = self.mocker.mock()
        request.body_file
        self.mocker.result(StringIO(body))
        service.request = request   
        
        self.mocker.replay()
        
        return service

class ExcludeWordsServicePostTest(ExcludeWordsServiceTest):
    def testMatch(self):
        self.prepareService(u'{"word":"南路"}').post()
        self.assertTrue(ExcludeWordCharCache.isStartWith(u"南路"))        
    

class ExcludeWordsServicePutTest(ExcludeWordsServiceTest, ExcludeWordTest):
    excludeWords = u'{"words": ["路", "中路", "中路", "西路", "中街", "西街路口"]}'

    def setUp(self):
        BaseTestCase.setUp(self)             
        self.prepareService(self.excludeWords).put()   
        
    
class ExcludeWordCacheTest(BaseTestCase, ExcludeWordTest):    
    def setUp(self):
        BaseTestCase.setUp(self)
        for word in excludeWords:
            ExcludeWordCharCache.put(word)      
        