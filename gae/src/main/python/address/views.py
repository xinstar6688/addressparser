from address.models import Area
from rest import Resource

class AreaDetail(Resource):
    def setProperty(self, areaCode):
        self.areaCode = areaCode
        
    def getResource(self):
        return Area.getByCode(self.areaCode)
    
    def newResource(self):
        return Area(code = self.areaCode)
    
    def deleteResource(self, resource):
        resource.delete();
    
    def getUri(self):
        return "/areas/%s" % (self.code)
    
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
