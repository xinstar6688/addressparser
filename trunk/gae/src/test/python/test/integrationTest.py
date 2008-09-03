# -*- coding: utf-8 -*-

from unittest import TestCase
import httplib

conn = httplib.HTTPConnection("localhost:8080")
headers = {"Content-type": "application/json"}

class ExcludeWordsServiceTest(TestCase):    
    def testPut(self):
        conn.request("PUT", "/excludeWords", 
                     '{"words": ["路","中路","中路","西路","中街","西街路口"]}', 
                     headers)
        response = conn.getresponse()
        self.assertEqual(204, response.status)
        
    def testPost(self):
        conn.request("POST", "/excludeWords", '{"word": "南路"}', headers)
        response = conn.getresponse()
        self.assertEqual(204, response.status)
        

class AreasServiceTest(TestCase):
    def testDelete(self):
        conn.request("DELETE", "/areas")
        response = conn.getresponse()
        self.assertEqual(204, response.status)        
