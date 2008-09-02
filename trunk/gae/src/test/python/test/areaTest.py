# -*- coding: utf-8 -*-

from StringIO import StringIO
from address.models import AreaCache
from address.services import AreaImporter
from google.appengine.api import memcache
from test import BaseTestCase, areas

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
    def setUp(self):
        BaseTestCase.setUp(self)
        for area in areas:
            AreaCache.put(area)
                  
    def testGetParent(self):
        self.assertEqual(areas[0], AreaCache.getParent(areas[1]))
        
    def testEmptyReader(self):
        self.assertEquals(0, len(AreaCache.getMatchedCities("")));


    def testPartMatch(self):
        self.assertEquals(0, len(AreaCache.getMatchedCities(u"杭")));
    

    def testMatchInMiddle(self):
        self.assertEquals(0, len(AreaCache.getMatchedCities(u"大杭州市")));
    

    def testNoOverlap(self):
        self.assertEquals(areas[1], AreaCache.getMatchedCities(u"杭州")[0]);
    

    def testOverlap(self):
        self.assertEquals(areas[3], AreaCache.getMatchedCities(u"南昌")[0]);
    

    def testLongest(self):
        self.assertEquals(areas[4], AreaCache.getMatchedCities(u"南昌西北")[0]);
    

    def testSameName(self):
        cities = AreaCache.getMatchedCities(u"南京");
        self.assertEquals(areas[7], cities[0]);
        self.assertEquals(areas[10], cities[1]);
        