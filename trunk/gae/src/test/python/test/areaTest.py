# -*- coding: utf-8 -*-

from StringIO import StringIO
from address.models import AreaCache
from address.services import AreaImporter
from google.appengine.api import memcache
from test import BaseTestCase

class AreaImporterTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)             

    def prepareImporter(self, body):
        importer = AreaImporter()
    
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
    
    def testMatch(self):
        self.prepareImporter(u'{"middle": null, "code": "110000", "name": "北京", "unit": "市", "hasChild" : true}').post()
        areas = AreaCache.getMatchedCities(u"北京")
        self.assertEqual(1, len(areas)); 
        
    def testClear(self):
        importer = AreaImporter(); 
          
        response = self.mocker.mock()
        response.set_status(204)
        importer.response = response
        self.mocker.replay()

        importer.delete()
        
        self.assertEqual(None, memcache.get("address.models.Area.cache"))
 
class AreaCacheTest(BaseTestCase):        
    areas = [{"code" : "100000", "name" : u"浙江", "unit" : u"省", "hasChild" : True}, 
         {"code" : "101000" , "name" : u"杭州", "unit" : u"市", "parent" : "100000", "hasChild" : False},
         {"code" : "200000", "name" : u"江西", "unit" : u"省", "hasChild" : True}, 
         {"code" : "201000" , "name" : u"南昌", "unit" : u"市", "parent" : "200000", "hasChild" : True},
         {"code" : "201010" , "name" : u"南昌西北", "unit":"区", "parent" : "201000", "hasChild" : False},
         {"code" : "202000" , "name" : u"南", "unit":"市", "parent" : "200000", "hasChild" : False},
         {"code" : "300000", "name" : u"江苏", "unit" : u"省", "hasChild" : True}, 
         {"code" : "301000" , "name" : u"南京", "unit" : u"市", "parent" : "300000", "hasChild" : True},
         {"code" : "301010" , "name" : u"南京西", "unit" : u"区", "parent" : "301000", "hasChild" : False},
         {"code" : "400000", "name" : u"湖南", "unit" : u"省", "hasChild" : True}, 
         {"code" : "401000" , "name" : u"南京", "unit" : u"市", "parent" : "400000", "hasChild" : False},
         {"code" : "500000", "name" : u"吉林", "unit" : u"省", "hasChild" : True}, 
         {"code" : "501000" , "name" : u"吉林", "unit" : u"市", "parent" : "500000", "hasChild" : True},
         {"code" : "502000" , "name" : u"长春", "unit" : u"市", "parent" : "500000", "hasChild" : False}]

    def setUp(self):
        BaseTestCase.setUp(self)
        for area in self.areas:
            AreaCache.put(area)
                  
    def testGetParent(self):
        self.assertEqual(self.areas[0], AreaCache.getParent(self.areas[1]))
        
    def testEmptyReader(self):
        self.assertEquals(0, len(AreaCache.getMatchedCities("")));


    def testPartMatch(self):
        self.assertEquals(0, len(AreaCache.getMatchedCities(u"杭")));
    

    def testMatchInMiddle(self):
        self.assertEquals(0, len(AreaCache.getMatchedCities(u"大杭州市")));
    

    def testNoOverlap(self):
        self.assertEquals(self.areas[1], AreaCache.getMatchedCities(u"杭州")[0]);
    

    def testOverlap(self):
        self.assertEquals(self.areas[3], AreaCache.getMatchedCities(u"南昌")[0]);
    

    def testLongest(self):
        self.assertEquals(self.areas[4], AreaCache.getMatchedCities(u"南昌西北")[0]);
    

    def testSameName(self):
        cities = AreaCache.getMatchedCities(u"南京");
        self.assertEquals(self.areas[7], cities[0]);
        self.assertEquals(self.areas[10], cities[1]);
        