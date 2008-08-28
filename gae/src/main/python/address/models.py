from appengine_django.models import BaseModel
from google.appengine.ext import db

class Area(BaseModel):
    code = db.StringProperty(required=True)
    name = db.StringProperty()
    middle = db.StringProperty()
    unit = db.StringProperty()
    parentArea = db.SelfReferenceProperty(collection_name = "children")
    
    def hasChild(self):
        return len(self.children) > 0
    
    @classmethod
    def getByCode(cls, code):
        return cls.gql("WHERE code=:1", code).get()
    
class ExcludeWord(BaseModel):
    word = db.StringProperty()
