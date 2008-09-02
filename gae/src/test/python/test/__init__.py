# -*- coding: utf-8 -*-

from google.appengine.api import apiproxy_stub_map, datastore_file_stub, \
    user_service_stub, urlfetch_stub, mail_stub
from google.appengine.api.memcache import memcache_stub
from unittest import TestCase
from mocker import MockerTestCase
import os

class BaseTestCase(MockerTestCase):
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

excludeWords = [u"路", u"中路", u"中路", u"西路", u"中街", u"西街路口"]
