from address.models import ExcludeWordCache, AreaCache
from django.utils import simplejson
from google.appengine.ext.webapp import RequestHandler
from address.models import AreaParser 
import logging

def toJson(area):
    values = {}
    
    values["code"] = '"%s"' % area["code"]
    values["name"] = '"%s"' % AreaCache.getAreaName(area)
    
    parent = AreaCache.getParent(area)
    if parent:
        values["parent"] = toJson(parent)
        
    return "{%s}" % ",".join(['"%s":%s' % (k,v) for k,v in values.items()])

class AreaResource(RequestHandler):
    def get(self, code):
        area = AreaCache.getArea(code)
        self.response.out.write(toJson(area));

class AreaParserService(RequestHandler):
    def get(self):
        address = self.request.get("q")
        logging.info("parsing %s" % address)
        areas = AreaParser.parse(address)
        body = '{"areas":[%s]}' % ",".join([toJson(area) for area in areas])
        self.response.out.write(body);
        
    
class AreasService(RequestHandler):
    def get(self):
        self.response.out.write(str(AreaCache.getCache()));
    
    def post(self):
        try:
            area = simplejson.load(self.request.body_file) 
        except (ValueError, TypeError, IndexError):
            self.response.set_status(400)
            return
        
        AreaCache.put(area);
        self.response.set_status(204)
        
    def delete(self):
        AreaCache.clear()
        self.response.set_status(204)
        
class ExcludeWordsService(RequestHandler):
    def put(self):
        try:
            words = simplejson.load(self.request.body_file)["words"] 
        except (ValueError, TypeError, IndexError):
            self.response.set_status(400)
            return
        
        ExcludeWordCache.clear()
        for word in words:
            ExcludeWordCache.put(word);
            
        self.response.set_status(204)
    
    def post(self):
        try:
            word = simplejson.load(self.request.body_file)["word"] 
        except (ValueError, TypeError, IndexError):
            self.response.set_status(400)
            return
        
        ExcludeWordCache.put(word);
        self.response.set_status(204)
        