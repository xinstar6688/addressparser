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
