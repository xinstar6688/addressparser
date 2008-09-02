from address.models import ExcludeWordCache, AreaCache
from django.utils import simplejson
from google.appengine.ext.webapp import RequestHandler
from address.models import AreaParser  
import urllib

class AreaParserService(RequestHandler):
    def get(self):
        areas = AreaParser.parse(self.request.get("q"))
        body = '{"areas":[%s]}' % ",".join([self.toJson(area) for area in areas])
        self.response.out.write(body);
        
    def toJson(self, area):
        values = {}
        
        values["code"] = '"%s"' % area["code"]
        values["name"] = '"%s"' % AreaCache.getAreaName(area)
        
        parent = AreaCache.getParent(area)
        if parent:
            values["parent"] = self.toJson(parent)
            
        return "{%s}" % ",".join(['"%s":%s' % (k,v) for k,v in values.items()])
    
class AreasService(RequestHandler):
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
        