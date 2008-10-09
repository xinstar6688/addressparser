# -*- coding: utf-8 -*-

from StringIO import StringIO
from address.caches import AreaCharCache
from address.models import Area
from address.services import AreasService
from google.appengine.api import memcache
from test import BaseTestCase, areas

class AreaTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        for area in areas:
            area.put()
            
    def testGetParent(self):
        self.assertEqual(areas[0].code, areas[1].getParent().code)
        
    def testGetFullName(self):
        self.assertEqual(u"浙江省", areas[0].getFullName())
        
    def testGetByCode(self):
        self.assertEqual(u"浙江", Area.getByCode("100000").name)

class AreasServiceTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)             

    def prepareService(self, body):
        service = AreasService()
    
        response = self.mocker.mock()
        response.set_status(201)
        service.response = response
        
        headers = self.mocker.mock()
        response.headers
        self.mocker.result(headers)
        headers['Location'] = u'/areas/110000'
       
        request = self.mocker.mock()
        request.body_file
        self.mocker.result(StringIO(body))
        service.request = request  
        
        self.mocker.replay()
        
        return service
    
    def testMatch(self):
        self.prepareService(u'{"middle": null, "code": "110000", "name": "北京", "unit": "市", "hasChild" : true}').post()
        areas = AreaCharCache.getMatchedAreas(u"北京")
        self.assertEqual(1, len(areas)); 
 
class AreaCacheTest(BaseTestCase):        
    def setUp(self):
        BaseTestCase.setUp(self)
        for area in areas:
            area.put()
        
    def testEmptyReader(self):
        self.assertEquals(0, len(AreaCharCache.getMatchedAreas("")));


    def testPartMatch(self):
        self.assertEquals(0, len(AreaCharCache.getMatchedAreas(u"杭")));
    

    def testMatchInMiddle(self):
        self.assertEquals(0, len(AreaCharCache.getMatchedAreas(u"大杭州市")));
    

    def testNoOverlap(self):
        self.assertEquals(areas[1].code, AreaCharCache.getMatchedAreas(u"杭州")[0]);
    

    def testOverlap(self):
        self.assertEquals(areas[3].code, AreaCharCache.getMatchedAreas(u"南昌")[0]);
    

    def testLongest(self):
        self.assertEquals(areas[4].code, AreaCharCache.getMatchedAreas(u"南昌西北")[0]);
    

    def testSameName(self):
        cities = AreaCharCache.getMatchedAreas(u"南京");
        self.assertEquals(areas[7].code, cities[0]);
        self.assertEquals(areas[10].code, cities[1]);
        