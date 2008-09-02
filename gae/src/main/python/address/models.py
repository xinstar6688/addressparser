class AbstractCache:   
    _cache = {}
    
    @classmethod
    def getCache(cls):
        return cls._cache
    
    @classmethod
    def clear(cls):
        cls._cache.clear()
        
    @classmethod
    def put(cls, obj):
        cls.doPut(obj, cls.getCache(), cls.getCacheString(obj))

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
    areas = {}
    
    @classmethod
    def getParent(cls, obj):
        parent = obj.get("parent", None)
        if parent:
            return cls.areas[parent]        
    
    @classmethod
    def put(cls, obj):
        cls.doPut(obj, cls.getCache(), cls.getCacheString(obj))
        
        parentArea = cls.getParent(obj)
        if parentArea:
            parentArea["hasChild"] = True
            
        obj["hasChild"] = False
        cls.areas[obj["code"]] = obj

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
