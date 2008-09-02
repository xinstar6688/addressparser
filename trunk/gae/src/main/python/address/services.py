from address.cache import ExcludeWordCache
from address.models import Area
from django.utils import simplejson
from google.appengine.ext.webapp import RequestHandler
from rest import Resource

class AreaParser(RequestHandler):
    def get(self):
        areas = Area.parse(self.request.get("q"))
        
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

class AreaResource(Resource):
    def setProperty(self, areaCode):
        self.areaCode = areaCode
        
    def getResource(self):
        return Area.getByCode(self.areaCode)
    
    def newResource(self):
        return Area(code = self.areaCode)
    
    def deleteResource(self, resource):
        resource.delete();
    
    def getUri(self):
        return "/areas/%s" % (self.areaCode)
    
    def getFieldLoader(self):
        def loadParent(obj, field, newVal):
            parentArea = Area.getByCode(newVal)
            setattr(obj, field, parentArea)  
        return {"parentArea" : loadParent}
            
    def getFieldsDumper(self): 
        def getParentCode(obj, field):
            parentArea = getattr(obj, field)
            if parentArea:
                return parentArea.code
        return {"parentArea" : getParentCode}
