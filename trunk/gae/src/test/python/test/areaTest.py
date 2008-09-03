# -*- coding: utf-8 -*-

from address.models import AreaCache, Area
from test import BaseTestCase, areas, entities

class AreaTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        for entity in entities:
            entity.save()
            
    def testGetParent(self):
        self.assertEqual(entities[0].code, entities[1].getParent().code)
        
    def testGetFullName(self):
        self.assertEqual(u"浙江省", entities[0].getFullName())
        
    def testGetByCode(self):
        self.assertEqual(u"浙江", Area.getByCode("100000").name)

class AreaCacheTest(BaseTestCase):        
    def setUp(self):
        BaseTestCase.setUp(self)
        for area in areas:
            AreaCache.put(area)
        for entity in entities:
            entity.save()
        
    def testEmptyReader(self):
        self.assertEquals(0, len(AreaCache.getMatchedAreas("")));


    def testPartMatch(self):
        self.assertEquals(0, len(AreaCache.getMatchedAreas(u"杭")));
    

    def testMatchInMiddle(self):
        self.assertEquals(0, len(AreaCache.getMatchedAreas(u"大杭州市")));
    

    def testNoOverlap(self):
        self.assertEquals(areas[1], AreaCache.getMatchedAreas(u"杭州")[0]);
    

    def testOverlap(self):
        self.assertEquals(areas[3], AreaCache.getMatchedAreas(u"南昌")[0]);
    

    def testLongest(self):
        self.assertEquals(areas[4], AreaCache.getMatchedAreas(u"南昌西北")[0]);
    

    def testSameName(self):
        cities = AreaCache.getMatchedAreas(u"南京");
        self.assertEquals(areas[7], cities[0]);
        self.assertEquals(areas[10], cities[1]);
        