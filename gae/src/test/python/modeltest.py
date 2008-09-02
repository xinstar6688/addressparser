# -*- coding: utf-8 -*-

from address.models import Area, AreaCache, ExcludeWordCache
from google.appengine.api import apiproxy_stub_map, datastore_file_stub, \
    user_service_stub, urlfetch_stub, mail_stub
from google.appengine.api.memcache import memcache_stub
from unittest import TestCase
import os

class BaseTestCase(TestCase):
    def setUp(self):     
        apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()  
  
        apiproxy_stub_map.apiproxy.RegisterStub('urlfetch', urlfetch_stub.URLFetchServiceStub())   
        apiproxy_stub_map.apiproxy.RegisterStub('mail', mail_stub.MailServiceStub())        
        apiproxy_stub_map.apiproxy.RegisterStub('memcache', memcache_stub.MemcacheServiceStub())   
        apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', datastore_file_stub.DatastoreFileStub(u'myTemporaryDataStorage', '/dev/null', '/dev/null'))    
        apiproxy_stub_map.apiproxy.RegisterStub('user', user_service_stub.UserServiceStub())  

        os.environ['AUTH_DOMAIN'] = 'gmail.com'  
        os.environ['USER_EMAIL'] = 'myself@appengineguy.com' 
        os.environ['SERVER_NAME'] = 'fakeserver.com'   
        os.environ['SERVER_PORT'] = '9999'    

class AreaCacheTest(BaseTestCase):        
    areas = [Area(code = "101000" , name = u"杭州", unit = u"市"),
             Area(code = "201000" , name = u"南昌", unit = u"市"),
             Area(code = "201010" , name = u"南昌西北", unit="区"),
             Area(code = "202000" , name = u"南", unit="市"),
             Area(code = "301000" , name = u"南京", unit = u"市"),
             Area(code = "301010" , name = u"南京西", unit = u"区"),
             Area(code = "401000" , name = u"南京", unit = u"市")]

    def setUp(self):
        BaseTestCase.setUp(self)
        for area in self.areas:
            AreaCache.put(area)
         
    def testEmptyReader(self):
        self.assertEquals(0, len(AreaCache.getMatchedCities("")));


    def testPartMatch(self):
        self.assertEquals(0, len(AreaCache.getMatchedCities(u"杭")));
    

    def testMatchInMiddle(self):
        self.assertEquals(0, len(AreaCache.getMatchedCities(u"大杭州市")));
    

    def testNoOverlap(self):
        self.assertEquals(self.areas[0], AreaCache.getMatchedCities(u"杭州")[0]);
    

    def testOverlap(self):
        self.assertEquals(self.areas[1], AreaCache.getMatchedCities(u"南昌")[0]);
    

    def testLongest(self):
        self.assertEquals(self.areas[2], AreaCache.getMatchedCities(u"南昌西北")[0]);
    

    def testSameName(self):
        cities = AreaCache.getMatchedCities(u"南京");
        self.assertEquals(self.areas[4], cities[0]);
        self.assertEquals(self.areas[6], cities[1]);
            
        
class ExcludeWordTest(BaseTestCase):
    excludeWords = [u"路", u"中路", u"中路", u"西路", u"中街", u"西街路口"]
    
    def setUp(self):
        TestCase.setUp(self)
        for word in self.excludeWords:
            ExcludeWordCache.put(word)      
    
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
            