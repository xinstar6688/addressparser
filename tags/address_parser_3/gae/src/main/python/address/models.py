# -*- coding: utf-8 -*-

from address.caches import AreaCharCache, ExcludeWordCharCache
from google.appengine.api import memcache
from google.appengine.ext import db
import logging

class Area(db.Model):
    code = db.StringProperty()
    name = db.StringProperty()
    parentArea = db.StringProperty()
    hasChild = db.BooleanProperty(default=False)
    alphaCode = db.StringProperty()
    pinyin = db.StringProperty()
    alias = db.StringListProperty(default = [])
    postCode = db.StringProperty()
    
    def getFullName(self):
        parent = self.getParent()
        if parent:
            return parent.getFullName() + self.name
        else:
            return self.name
        
    def put(self):
        area = self.getByCode(self.code)
         
        db.Model.put(self)
        AreaCache.set(self.code, self)
        AreaJsonCache.delete(self.code)
        
        if area: AreaCharCache.remove(area)
        AreaCharCache.put(self)
    
    @classmethod
    def deleteAll(cls):
        query = cls.all()
        while True:
            areas = query.fetch(100)
            for area in areas: 
                AreaCache.delete(area)
                area.delete()
            if len(areas) < 100: break
    
    @classmethod
    def clear(cls):
        cls.deleteAll()
        AreaCharCache.clear()

    @classmethod
    def getByCode(cls, code):
        area = AreaCache.get(code)
        if not area:
            area = cls.gql("where code = :1", code).get()
            AreaCache.set(code, area)
        return area
    
    def getParent(self):
        return self.getByCode(self.parentArea)
 
    def toJson(self):
        json = AreaJsonCache.get(self.code)
        if not json:
            values = {}       
            values["code"] = '"%s"' % self.code
            values["name"] = '"%s"' % self.name    
            values["postCode"] = '"%s"' % (self.postCode and self.postCode or "")
            parent = self.getParent()
            if parent: values["parentArea"] = parent.toJson()
                
            json = "{%s}" % ",".join(['"%s":%s' % (k,v) for k,v in values.items()])

        AreaJsonCache.set(self.code, json)
        return json

    def __cmp__(self, area):
        if isinstance(area, Area):
            return cmp(self.code, area.code)
        else:
            return False
        
class ExcludeWord(db.Model):
    word = db.StringProperty()
    
    def put(self):
        db.Model.put(self)
        ExcludeWordCharCache.put(self.word)

    @classmethod
    def deleteAll(cls):
        query = cls.all()
        while True:
            words = query.fetch(100)
            for word in words: word.delete()
            if len(words) < 100: break
    
    @classmethod
    def clear(cls):
        cls.deleteAll()
        ExcludeWordCharCache.clear()
        
class AbstractCache:   
    @classmethod
    def _getCacheName(cls, code):
        return "%s%s" % (cls._cachePrefix, code)

    @classmethod
    def get(cls, code):
        return memcache.get(cls._getCacheName(code))
    
    @classmethod
    def set(cls, code, obj):
        memcache.set(cls._getCacheName(code), obj)
        
    @classmethod
    def delete(cls, code):
        memcache.delete(cls._getCacheName(code))

class AreaCache(AbstractCache):
    _cachePrefix = "address.models.Area."
    
class AreaJsonCache(AbstractCache):
    _cachePrefix = "address.models.Area.json."

class AreaParser:
    @classmethod
    def parse(cls, address, parent = None):
        """ 从指定地址中分析出包含的区域
        """
        
        for i in range(len(address)):
            # 获取匹配的区域， 如果指定parent， 则匹配的区域必须是parent的下级区域
            (areas, depth) = AreaCharCache.getMatchedAreas(address[i:])
            areas = [Area.getByCode(code) for code in areas]
            areas = [area for area in areas if  (not parent) or cls._isChild(parent, area)]                       
            logging.debug("got areas[%s] for %s" % (",".join([area.name for area in areas]), address))
            
            if len(areas) > 0:
                followStart = i + depth                
               
                #如果区域后面跟着特定的词语，如”路“， 则忽略这个区域
                #如”湖南路“就不应该认为是”湖南省“
                if ExcludeWordCharCache.isStartWith(address[followStart:]): continue
                
                #如果区域还有下级区域的话，则在后面字符串中继续查找下级区域，然后用找到的下级区域代替上级区域
                childrenAreas = []
                for area in areas:
                    if area.hasChild:
                        children = cls.parse(address[followStart:], area)
                        if len(children) > 0: 
                            childrenAreas.extend(children)
                            
                if len(childrenAreas) > 0: areas = childrenAreas
                    
                logging.debug("got children areas[%s] for %s" % (",".join([area.name for area in areas]), address))
                     
                #如果在结果集中同时存在上级和下级区域，则去除上级区域                
                parentAreas = []
                for area in areas: parentAreas.extend(cls._getParents(area)) 
                 
                for area in parentAreas:
                    if area in areas:
                        areas.remove(area)   
                        
                logging.debug("areas[%s] after removed parents for %s" % (",".join([area.name for area in areas]), address))
                              
                #如果存在多个结果的时候，在后续字符中查找上级区域，找到的必然是正确的结果               
                if len(areas) > 1:
                    matchedParents = [area for area in areas if cls._hasParent(area, address[followStart:])]
                    if len(matchedParents) > 0: areas = matchedParents
                
                logging.debug("areas[%s] after matched parents for %s" % (",".join([area.name for area in areas]), address))

                return areas           
        return []

    @classmethod
    def _isChild(cls, parent, child):  
        """ 判断parent是否是child的上级区域
        """
        return parent in cls._getParents(child)      
    
    @classmethod
    def _getParents(cls, area):
        """ 获取指定区域的所有上级区域
        """
        parents = []
        parent = area.getParent();
        if parent:
            parents.append(parent)
            parents.extend(cls._getParents(parent))    
        return parents       
    
    @classmethod
    def _hasParent(cls, area, string):
        """ 在string中是否包含指定区域的上级区域
        """
        parents = cls._getParents(area)
        for parent in parents:   
            if cls._hasAreaName(parent.name, string):
                return True 
            if parent.alias:                                     
                for name in parent.alias:         
                    if cls._hasAreaName(name, string):
                        return True                                     
        return False
    
    @classmethod
    def _hasAreaName(cls, areaName, string):
        """ 判断在string中是否包含区域名称
        """
        position = string.find(areaName)
        if position >= 0:
            followString = string[position + len(areaName):]
            if ExcludeWordCharCache.isStartWith(followString):
                return cls._hasAreaName(areaName, followString)
            else:
                return True;
