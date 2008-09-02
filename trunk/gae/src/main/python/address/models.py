from google.appengine.api import memcache

class AreaParser:
    @classmethod
    def isChild(cls, parent, child):        
        if child.get("parent", None) == parent["code"] :
            return True
        
        father = AreaCache.getParent(child)
        if father:
            return father.get("parent", None) == parent["code"]
        return False
    
    @classmethod
    def getParents(cls, area):
        parents = []
        parent = AreaCache.getParent(area);
        if parent:
            parents.append(parent)
            parents.extend(cls.getParents(parent))    
        return parents    
    
    @classmethod
    def parse(cls, str, start = 0, parent = None):
        address = str[start:]
        for i in range(len(address)):
            cities = [city for city in AreaCache.getMatchedCities(address[i:]) if  (not parent) or cls.isChild(parent, city)]           
            
            if len(cities) > 0:
                followStart = start + i + len(cities[0]["name"])                
               
                if ExcludeWordCache.isStartWith(address[followStart:]):
                    continue
                
                norrowCities = []
                for city in cities:
                    if city["hasChild"]:
                        followCities = cls.parse(str, followStart, city)
                        if len(followCities) > 0: 
                            norrowCities.extend(followCities)
                if len(norrowCities) > 0:
                    cities = norrowCities
                                
                parentCities = []
                for city in cities:
                    parentCities.extend(cls.getParents(city)) 
                 
                for city in parentCities:
                    if city in cities:
                        cities.remove(city)   
                               
                if len(cities) > 1:
                    matchedProvicens = []
                    for city in cities:
                        if cls.hasMatchedProvicen(city, str[0:start + i]) or cls.hasMatchedProvicen(city, str[followStart:]):
                            matchedProvicens.append(city);

                    if len(matchedProvicens) > 0:
                        return matchedProvicens

                return cities
            
        return []
    
    @classmethod
    def hasMatchedProvicen(cls, city, string):
        parent = AreaCache.getParent(city)
        if parent:            
            if cls.hasMatchedParent(parent["name"], string):
                return True                                     
            else:
                return cls.hasMatchedProvicen(parent, string)
        return False
    
    @classmethod
    def hasMatchedParent(cls, parentName, string):
        position = string.find(parentName)
        if position >= 0:
            followString = string[position + len(parentName):]
            if ExcludeWordCache.isStartWith(followString):
                return cls.hasMatchedParent(parentName, followString)
            else:
                return True;
           
    
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
