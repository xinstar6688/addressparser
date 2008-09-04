# -*- coding: utf-8 -*-

from address.caches import AreaCache, ExcludeWordCache
from google.appengine.api import memcache
from google.appengine.ext import db
import logging

class Area(db.Model):
    code = db.StringProperty()
    name = db.StringProperty()
    middle = db.StringProperty()
    unit = db.StringProperty()
    parentArea = db.StringProperty()
    hasChild = db.BooleanProperty()
    
    def put(self):
        area = self.getByCode(self.code)
         
        db.Model.put(self)
        memcache.set(self._getCacheName(self.code), self)
        
        if not area:
            AreaCache.put(self)
        else:
            if area.name != self.name:
                AreaCache.remove(area)
                AreaCache.put(self)
        
    save = put
    
    @classmethod
    def _getCacheName(cls, code):
        return "address.models.Area.%s" % code
    
    @classmethod
    def getByCode(cls, code):
        area = memcache.get(cls._getCacheName(code))
        if not area:
            area = cls.gql("where code = :1", code).get()
            memcache.set(cls._getCacheName(code), area)
        return area
    
    def getParent(self):
        return self.getByCode(self.parentArea)
    
    def getFullName(self):
        return "%s%s%s" % (self.name, self.middle and self.middle or "",
                           self.unit and self.unit or "")

    def __cmp__(self, area):
        if isinstance(area, Area):
            return cmp(self.code, area.code)
        else:
            return False

class AreaParser:
    @classmethod
    def parse(cls, address, start = 0, parent = None):
        """ 从指定地址中分析出包含的区域
        """
        partAddress = address[start:]
        for i in range(len(partAddress)):
            # 获取匹配的区域， 如果指定parent， 则匹配的区域必须是parent的下级区域
            areas = [Area.getByCode(code) for code in AreaCache.getMatchedAreas(partAddress[i:])]
            areas = [area for area in areas if  (not parent) or cls.isChild(parent, area)]                       
            logging.debug("got areas[%s] for %s" % (",".join([area.name for area in areas]), address))
            
            if len(areas) > 0:
                followStart = i + len(areas[0].name)                
               
                #如果区域后面跟着特定的词语，如”路“， 则忽略这个区域
                #如”湖南路“就不应该认为是”湖南省“
                if ExcludeWordCache.isStartWith(partAddress[followStart:]):
                    continue
                
                #如果区域还有下级区域的话，则在后面字符串中继续查找下级区域，然后用找到的下级区域代替上级区域
                childrenAreas = []
                for area in areas:
                    if area.hasChild:
                        children = cls.parse(address, start + followStart, area)
                        if len(children) > 0: 
                            childrenAreas.extend(children)
                if len(childrenAreas) > 0:
                    areas = childrenAreas
                    logging.debug("got children areas[%s] for %s" % (",".join([area.name for area in areas]), address))
                     
                #如果在结果集中同时存在上级和下级区域，则去除上级区域                
                parentAreas = []
                for area in areas:
                    parentAreas.extend(cls.getParents(area)) 
                 
                for area in parentAreas:
                    if area in areas:
                        areas.remove(area)   
                        
                logging.debug("areas[%s] after removed parents for %s" % (",".join([area.name for area in areas]), address))
                              
                #如果存在多个结果的时候，在后续字符中查找上级区域，找到的必然是正确的结果               
                if len(areas) > 1:
                    matchedParents = []
                    for area in areas:
                        if cls.hasParent(area, address[followStart:]):
                            matchedParents.append(area);

                    if len(matchedParents) > 0:
                        logging.debug("areas[%s] after matched parents for %s" % (",".join([area.name for area in matchedParents]), address))
                        return matchedParents

                return areas
            
        return []

    @classmethod
    def isChild(cls, parent, child):  
        """ 判断parent是否是child的上级区域
        """
        return parent in cls.getParents(child)      
    
    @classmethod
    def getParents(cls, area):
        """ 获取指定区域的所有上级区域
        """
        parents = []
        parent = area.getParent();
        if parent:
            parents.append(parent)
            parents.extend(cls.getParents(parent))    
        return parents       
    
    @classmethod
    def hasParent(cls, area, string):
        """ 在string中是否包含指定区域的上级区域
        """
        parents = cls.getParents(area)
        for parent in parents:            
            if cls.hasAreaName(parent.name, string):
                return True                                     
        return False
    
    @classmethod
    def hasAreaName(cls, areaName, string):
        """ 判断在string中是否包含区域名称
        """
        position = string.find(areaName)
        if position >= 0:
            followString = string[position + len(areaName):]
            if ExcludeWordCache.isStartWith(followString):
                return cls.hasAreaName(areaName, followString)
            else:
                return True;
           
    
