# -*- coding: utf-8 -*-

from unittest import TestCase
import httplib

conn = httplib.HTTPConnection("localhost:8080")

class ExcludeWordImporterTest(TestCase):
    headers = {"Content-type": "application/json"}
    
    def testPut(self):
        conn.request("PUT", "/excludeWords", 
                     '{"words": ["路","中路","中路","西路","中街","西街路口"]}', 
                     self.headers)
        response = conn.getresponse()
        self.assertEqual(204, response.status)
        
    def testPost(self):
        conn.request("POST", "/excludeWords", '{"word": "南路"}', self.headers)
        response = conn.getresponse()
        self.assertEqual(204, response.status)
