# -*- coding: utf-8 -*-

from unittest import TestCase
import httplib

conn = httplib.HTTPConnection("localhost:8080")

class ExcludeWordImporterTest(TestCase):
    excludeWords = '{"words": ["路","中路","中路","西路","中街","西街路口"]}'
    headers = {"Content-type": "application/json"}
    
    def testImport(self):
        conn.request("PUT", "/excludeWords", self.excludeWords, self.headers)
        response = conn.getresponse()
        self.assertEqual(204, response.status)