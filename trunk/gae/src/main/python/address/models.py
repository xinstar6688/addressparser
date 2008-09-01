from google.appengine.ext import db
from google.appengine.api import memcache

class Area(db.Model):
    code = db.StringProperty(required=True)
    name = db.StringProperty()
    middle = db.StringProperty()
    unit = db.StringProperty()
    parentArea = db.SelfReferenceProperty(collection_name = "children")
    lastModified=db.DateTimeProperty(auto_now=True);
    
    def hasChild(self):
        return len(self.children) > 0
    
    @classmethod
    def getByCode(cls, code):
        return cls.gql("WHERE code=:1", code).get()
    
    def put(self):
        db.Model.save(self)
        areaMap = memcache.get("address.models.Area.areaMap")
        if not areaMap:
            areaMap = AreaMap()
            memcache.set("address.models.Area.areaMap", areaMap)
        areaMap.put(self)
        
    save = put 
    
    def delete(self):
        db.Model.delete(self)
        memcache.get("address.models.Area.areaMap").remove(self)
        
    def __cmp__(self, area):
        if isinstance(area, Area):
            return cmp(self.code, area.code)
        else:
            return False

class AreaMap():
    _holder = {}
     
    def put(self, area):
        self.doPut(area, self._holder, area.name)         
        
    def doPut(self, area, parentMap, part):
        if len(part) == 0:
            if not parentMap.has_key(""):
                parentMap[""] = []
            parentMap[""].append(area)
        else:
            char = part[0]
            if not parentMap.has_key(char):
                parentMap[char] = {} 
            self.doPut(area, parentMap[char], part[1:])         
        
    def remove(self, area):
        self.doRemove(area, self._holder, area.name)     
        
    def doRemove(self, area, parentMap, part):
        if len(part) == 0:
            areas  = parentMap[""]
            areas.remove(area)
            if len(areas) == 0:
                del parentMap[""]
        else:
            char = part[0]
            childMap = parentMap[char]
            self.doRemove(area, childMap, part[1:])
            if len(childMap):
                del parentMap[char]
                
class ExcludeWord(db.Model):
    word = db.StringProperty()
