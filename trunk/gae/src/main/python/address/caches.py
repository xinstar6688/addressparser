# -*- coding: utf-8 -*-

from google.appengine.api import memcache

class AbstractCharCache:   
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
    
    
class AreaCharCache(AbstractCharCache):
    _charCacheName = "address.models.Area.cache.chars"
    
    @classmethod
    def getCache(cls, char):
        areaCache = memcache.get(cls.getCacheName(char))
        return areaCache and areaCache or {}
    
    @classmethod
    def setCache(cls, char, areaCache):
        memcache.set(cls.getCacheName(char), areaCache)

        charCache = memcache.get(cls._charCacheName)
        charCache = charCache and charCache or []
        if  char not in charCache:
            charCache.append(char)
            memcache.set(cls._charCacheName, charCache)
           
    @classmethod
    def deleteCache(cls, char):
        memcache.delete(cls.getCacheName(char))
        
    @classmethod
    def clear(cls):
        charCache = memcache.get(cls._charCacheName)
        if not charCache: return
        
        for char in charCache:
            cls.deleteCache(char)
        memcache.delete(cls._charCacheName)
        
    @classmethod
    def getCacheName(cls, char):
        return "address.models.Area.cache.%s" % char

    @classmethod
    def put(cls, obj):
        name = obj.alias
        char = name[:1]
        cache = cls.getCache(char)
        cls.doPut(obj, cache, name)
        cls.setCache(char, cache)  

    @classmethod
    def doInPut(cls, parentMap, obj):
        if not parentMap.has_key(""):
            parentMap[""] = []
        code = obj.code
        map = parentMap[""]
        if code not in map:
            map.append(code)        

    @classmethod
    def remove(cls, obj):
        name = obj.alias
        char = name[:1]
        cache = cls.getCache(char)
        cls.doRemove(obj, cache, name)   
        
        if len(cache) > 0:  
            cls.setCache(char, cache)  
        else:
            cls.deleteCache(char) 
        
    @classmethod
    def doRemove(cls, obj, parentMap, part):
        if len(part) == 0:
            cls.doInRemove(parentMap, obj)
        else:
            char = part[0]
            childMap = parentMap.get(char, None)
            if childMap:
                cls.doRemove(obj, childMap, part[1:])
                if len(childMap) == 0:
                    del parentMap[char]
                
    @classmethod
    def doInRemove(cls, parentMap, obj):
        areas  = parentMap[""]
        areas.remove(obj.code)
        if len(areas) == 0:
            del parentMap[""]
                
    @classmethod
    def getMatchedAreas(cls, address):
        return cls.doGetMatchedAreas(cls.getCache(address[:1]), address)

    @classmethod
    def doGetMatchedAreas(cls, areaMap, address):
        cities = []
        if len(address) > 0:
            char = address[0]
            if areaMap.has_key(char):
                cities = cls.doGetMatchedAreas(areaMap[char], address[1:])

        if len(cities) == 0 and areaMap.has_key(""):
            cities = areaMap[""]
        return cities
                

class ExcludeWordCharCache(AbstractCharCache):
    _cacheName = "address.models.ExcludeWord.cache"
    
    @classmethod
    def getCache(cls):
        areaCache = memcache.get(cls._cacheName)
        return areaCache and areaCache or {}
    
    @classmethod
    def setCache(cls, areaCache):
        memcache.set(cls._cacheName, areaCache)
        
    @classmethod
    def clear(cls):
        memcache.delete(cls._cacheName)

    @classmethod
    def isStartWith(cls, address):
        return cls.doIsStartWith(cls.getCache(), address);

    @classmethod
    def doIsStartWith(cls, excludeWordMap, address):
        result = False
        
        #这里有bug
        if len(excludeWordMap) == 0:
            result = True
            
        if len(address) > 0:
            char = address[0]
            if excludeWordMap.has_key(char):
                result = cls.doIsStartWith(excludeWordMap[char], address[1:])
            
        return result    
