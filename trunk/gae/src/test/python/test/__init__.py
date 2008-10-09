# -*- coding: utf-8 -*-

from address.models import Area, Address
from google.appengine.api import apiproxy_stub_map, datastore_file_stub, \
    user_service_stub, urlfetch_stub, mail_stub
from google.appengine.api.memcache import memcache_stub
from mocker import MockerTestCase
from unittest import TestCase
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

areas = [Area(code = u"100000", alias = [u"浙江"], name = u"浙江省", hasChild = True, alphaCode="AA"), 
     Area(code = u"101000" , alias = [u"杭州"], name = u"杭州市", parentArea = "100000", hasChild = False, alphaCode="AB"),
     Area(code = u"200000", alias = [u"江西"], name = u"江西省", hasChild = True, alphaCode="BA"), 
     Area(code = u"201000" , alias = [u"南昌"], name = u"南昌市", parentArea = "200000", hasChild = True, alphaCode="BB"),
     Area(code = u"201010" , alias = [u"南昌西北"], name=u"南昌西北区", parentArea = "201000", hasChild = False, alphaCode="BC"),
     Area(code = u"202000" , alias = [u"南"], name=u"南市", parentArea = "200000", hasChild = False, alphaCode="BD"),
     Area(code = u"300000", alias = [u"江苏"], name = u"江苏省", hasChild = True, alphaCode="CA"), 
     Area(code = u"301000" , alias = [u"南京"], name = u"南京市", parentArea = "300000", hasChild = True, alphaCode="CB"),
     Area(code = u"301010" , alias = [u"南京西"], name = u"南京西区", parentArea = "301000", hasChild = False, alphaCode="CC"),
     Area(code = u"400000", alias = [u"湖南"], name = u"湖南省", hasChild = True, alphaCode="DA"), 
     Area(code = u"401000" , alias = [u"南京"], name = u"南京市", parentArea = "400000", hasChild = False, alphaCode="DB"),
     Area(code = u"500000", alias = [u"吉林"], name = u"吉林省", hasChild = True, alphaCode="EA"), 
     Area(code = u"501000" , alias = [u"吉林"], name = u"吉林市", parentArea = "500000", hasChild = True, alphaCode="EB"),
     Area(code = u"502000" , alias = [u"长春"], name = u"长春市", parentArea = "500000", hasChild = False, postCode = "330000", alphaCode="EC")]

address = Address(name = u"上海市天山路600号")

excludeWords = [u"路", u"中路", u"中路", u"西路", u"中街", u"西街路口"]
