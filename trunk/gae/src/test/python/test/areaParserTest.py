# -*- coding: utf-8 -*-

from address.models import AreaCache, ExcludeWordCache, AreaParser
from test import BaseTestCase, areas, excludeWords

class AreaParserTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        for area in areas:
            AreaCache.put(area)
        for word in excludeWords:
            ExcludeWordCache.put(word)      

    def testEmpty(self):
        self.assertEquals(0, len(AreaParser.parse(u"")))
    
    def testNoMatched(self):
        self.assertEquals(0, len(AreaParser.parse(u"上海市天山路600号")))
    
    def testNormal(self):
        cities = AreaParser.parse(u"湖墅南路234号, 杭州市")
        self.assertEquals(1, len(cities))
        self.assertEquals(areas[1], cities[0])    

    def testExcluded4City(self):
        self.assertEquals(0, len(AreaParser.parse(u"杭州中路234号")))
    
    def testSameName(self):
        cities = AreaParser.parse(u"南京市XXX路234号")
        self.assertEquals(2, len(cities))
        self.assertEquals(areas[7], cities[0])
        self.assertEquals(areas[10], cities[1])   

    def testProvicen(self):
        cities = AreaParser.parse(u"南京市XXX路234号,江苏")
        self.assertEquals(1, len(cities))
        self.assertEquals(areas[7], cities[0])
    
    def testExcluded4Provicen(self):
        cities = AreaParser.parse(u"南京市湖南路234号,江苏")
        self.assertEquals(1, len(cities))
        self.assertEquals(areas[7], cities[0])
    
    def testTwoProvicen(self):
        cities = AreaParser.parse(u"江苏南京市XXX路234号, 湖南")
        self.assertEquals(1, len(cities))
        self.assertEquals(areas[7], cities[0]) 

    def testSpicialProvicen(self):
        cities = AreaParser.parse(u"吉林长春XXX路234号")
        self.assertEquals(1, len(cities))
        self.assertEquals(areas[13], cities[0])
    
    def testSpicialProvicenWithNoMatch(self):
        cities = AreaParser.parse(u"吉林XXX路234号")
        self.assertEquals(1, len(cities))
        self.assertEquals(areas[12], cities[0])
    
    def testPartSpicialProvicen(self):
        cities = AreaParser.parse(u"湖南南京市XXX路234号")
        self.assertEquals(1, len(cities))
        self.assertEquals(areas[10], cities[0])
    