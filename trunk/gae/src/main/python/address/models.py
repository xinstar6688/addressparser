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
        AreaCache.put(self)
    
    def delete(self):
        db.Model.delete(self)
        AreaCache.remove(self)
        
    def __cmp__(self, area):
        if isinstance(area, Area):
            return cmp(self.code, area.code)
        else:
            return False

class AbstractCache:   
    @classmethod
    def getCache(cls):
        areaCache = memcache.get(cls.cacheName)
        return areaCache and areaCache or {}
    
    @classmethod
    def setCache(cls, areaCache):
        memcache.set(cls.cacheName, areaCache)
        
    @classmethod
    def put(cls, obj):
        cache = cls.getCache()
        cls.doPut(obj, cache, cls.getCacheString(obj))
        cls.setCache(cache)             

    @classmethod
    def getCacheString(cls, obj):
        return obj
        
    @classmethod
    def doPut(cls, obj, parentMap, part):
        if len(part) == 0:
            cls.doInPut(parentMap, obj)
        else:
            char = part[0]
            if not parentMap.has_key(char):
                parentMap[char] = {} 
            cls.doPut(obj, parentMap[char], part[1:]) 
    
    @classmethod
    def doInPut(cls, parentMap, obj):
        pass        
    
        
    @classmethod
    def remove(cls, obj):
        cache = cls.getCache()
        cls.doRemove(obj, cache, cls.getCacheString(obj))     
        cls.setCache(cache)   
        
    @classmethod
    def doRemove(cls, obj, parentMap, part):
        if len(part) == 0:
            cls.doInRemove(parentMap, obj)
        else:
            char = part[0]
            childMap = parentMap[char]
            cls.doRemove(obj, childMap, part[1:])
            if len(childMap) == 0:
                del parentMap[char]
                
    @classmethod
    def doInRemove(cls, parentMap, obj):
        pass
    
class AreaCache(AbstractCache):
    cacheName = "address.models.Area.cache"
    
    @classmethod
    def put(cls, obj):
        cache = cls.getCache()
        cls.doPut(obj, cache, cls.getCacheString(obj))
        cls.setCache(cache)             

    @classmethod
    def getCacheString(cls, obj):
        return obj.name
        
    @classmethod
    def doPut(cls, obj, parentMap, part):
        if len(part) == 0:
            cls.doInPut(parentMap, obj)
        else:
            char = part[0]
            if not parentMap.has_key(char):
                parentMap[char] = {} 
            cls.doPut(obj, parentMap[char], part[1:]) 
    
    @classmethod
    def doInPut(cls, parentMap, obj):
        if not parentMap.has_key(""):
            parentMap[""] = []
        parentMap[""].append(obj)        

    @classmethod
    def doInRemove(cls, parentMap, obj):
        areas  = parentMap[""]
        areas.remove(obj)
        if len(areas) == 0:
            del parentMap[""]
                
    @classmethod
    def getMatchedCities(cls, address):
        return cls.doGetMatchedCities(cls.getCache(), address)

    @classmethod
    def doGetMatchedCities(cls, areaMap, address):
        cities = []
        if len(address) > 0:
            char = address[0]
            if areaMap.has_key(char):
                cities = cls.doGetMatchedCities(areaMap[char], address[1:])

        if len(cities) == 0 and areaMap.has_key(""):
            cities = areaMap[""]
        return cities
                
class ExcludeWord(db.Model):
    word = db.StringProperty()

class ExcludeWordCache(AbstractCache):
    cacheName = "address.models.ExcludeWord.cache"
    
    @classmethod
    def isStartWith(cls, address):
        return cls.doIsStartWith(cls.getCache(), address);

    @classmethod
    def doIsStartWith(cls, excludeWordMap, address):
        result = False
        
        if len(excludeWordMap) == 0:
            result = True
            
        if len(address) > 0:
            char = address[0]
            if excludeWordMap.has_key(char):
                result = cls.doIsStartWith(excludeWordMap[char], address[1:])
            
        return result    
