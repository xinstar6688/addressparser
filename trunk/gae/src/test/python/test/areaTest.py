# -*- coding: utf-8 -*-

from address.cache import AreaCache
from address.models import Area
from test import BaseTestCase
 
class AreaTest(BaseTestCase):
    areas = [Area(code = "100000", name = u"浙江", unit = u"省"), 
         Area(code = "101000" , name = u"杭州", unit = u"市", parentArea = "100000"),
         Area(code = "200000", name = u"江西", unit = u"省"), 
         Area(code = "201000" , name = u"南昌", unit = u"市", parentArea = "200000"),
         Area(code = "201010" , name = u"南昌西北", unit="区", parentArea = "201000"),
         Area(code = "202000" , name = u"南", unit="市", parentArea = "200000"),
         Area(code = "300000", name = u"江苏", unit = u"省"), 
         Area(code = "301000" , name = u"南京", unit = u"市", parentArea = "300000"),
         Area(code = "301010" , name = u"南京西", unit = u"区", parentArea = "301000"),
         Area(code = "400000", name = u"湖南", unit = u"省"), 
         Area(code = "401000" , name = u"南京", unit = u"市", parentArea = "400000"),
         Area(code = "500000", name = u"吉林", unit = u"省"), 
         Area(code = "501000" , name = u"吉林", unit = u"市", parentArea = "500000"),
         Area(code = "502000" , name = u"长春", unit = u"市", parentArea = "500000")]

    excludeWords = [u"路", u"中路", u"中路", u"西路", u"中街", u"西街路口"]

    def setUp(self):
        BaseTestCase.setUp(self)
        for area in self.areas:
            area.save()    
            
            
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
        