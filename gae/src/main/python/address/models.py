from address.cache import AreaCache
from google.appengine.ext import db

class Area(db.Model):
    code = db.StringProperty(required=True)
    name = db.StringProperty()
    middle = db.StringProperty()
    unit = db.StringProperty()
    parentArea = db.SelfReferenceProperty(collection_name = "children")
    lastModified = db.DateTimeProperty(auto_now=True);
    
    @classmethod
    def getByCode(cls, code):
        return cls.gql("WHERE code=:1", code).get()
    
    @classmethod
    def parse(cls, address):
        pass
    
    def hasChild(self):
        return len(self.children) > 0
    
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

class ExcludeWord(db.Model):
    word = db.StringProperty()
