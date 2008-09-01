from address.models import Area
from google.appengine.ext.webapp import RequestHandler
from rest import Resource

class AreaParser(RequestHandler):
    def get(self):
        address = self.request.get("q")
        print address

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
