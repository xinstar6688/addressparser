from google.appengine.api import memcache
class AbstractCache:   
    @classmethod
    def getCache(cls):
        areaCache = memcache.get(cls.cacheName)
        return areaCache and areaCache or {}
    
    @classmethod
    def setCache(cls, areaCache):
        memcache.set(cls.cacheName, areaCache)
        
    @classmethod
    def clear(cls):
        memcache.delete(cls.cacheName)
        
    @classmethod
    def put(cls, obj):
        cache = cls.getCache()
        cls.doPut(obj, cache, cls.getCacheString(obj))
        cls.doPostPut(obj, cache)
        cls.setCache(cache)  
        
    @classmethod
    def doPostPut(cls, obj, cache):
        pass           

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
    
    
class AreaCache(AbstractCache):
    cacheName = "address.models.Area.cache"
    
    @classmethod
    def getParent(cls, obj):
        parent = obj.get("parent", None)
        if parent:
            return cls.getAreas(cls.getCache())[parent]        
    
    @classmethod
    def getAreas(cls, cache):
        if not cache.has_key("_areas"):
            cache["_areas"] = {}
        return cache["_areas"]
    
    @classmethod
    def doPostPut(cls, obj, cache):
        areas = cls.getAreas(cache)
        areas[obj["code"]] = obj

    @classmethod
    def getCacheString(cls, obj):
        return obj["name"]

    @classmethod
    def doInPut(cls, parentMap, obj):
        if not parentMap.has_key(""):
            parentMap[""] = []
        parentMap[""].append(obj)        
                
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
