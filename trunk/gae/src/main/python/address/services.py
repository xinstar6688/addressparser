from address.models import ExcludeWordCache, AreaCache
from django.utils import simplejson
from google.appengine.ext.webapp import RequestHandler

class AreaParser(RequestHandler):
    def get(self):
        self.request.get("q")
    
class AreaImporter(RequestHandler):
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
        
class ExcludeWordImporter(RequestHandler):
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
