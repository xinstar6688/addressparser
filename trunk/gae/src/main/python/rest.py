from StringIO import StringIO
from django.utils import simplejson
from google.appengine.api import memcache
from google.appengine.ext.webapp import RequestHandler

class Resource(RequestHandler):  
    def setProperty(self, *args):
        pass
    
    def isUnmodified(self, resource):
        etag = self.request.headers.get("ETag", None)
        if etag and etag == getattr(resource, self.eTagField, None):
            return True
        lastModified = self.request.headers.get("Last-Modified", None)
        if lastModified:
            oldLastModified = getattr(resource, self.lastModifiedField, None) 
            if oldLastModified and oldLastModified.strftime("%a, %d %b %Y %H:%M:%S GMT"):
                return True
        return False
    
    lastModifiedField = "lastModified"
    eTagField = "eTag"
    hiddenFields = (lastModifiedField, eTagField)
    def setConditional(self, resource):
        lastModified = getattr(resource, self.lastModifiedField, None)
        if lastModified:
            self.response.headers["Last-Modified"] = lastModified.strftime("%a, %d %b %Y %H:%M:%S GMT")           
        eTag = getattr(resource, self.eTagField, None)
        if eTag:
            self.response.headers["ETag"] = eTag      

    caching = True
    cacheTime = 300
    def get(self, args):
        self.setProperty(args);
        
        if self.caching:
            resource = memcache.get(self.request.uri)
            if resource:
                if self.isUnmodified(resource):
                    self.response.set_status(304)
                    return
                self.writeToResponse(resource)
                return

        # Look up the area (possibly throwing a 404)
        resource =  self.getResource()   
        if not resource:
            self.response.set_status(404)
            return
        self.writeToResponse(resource)
        
        if self.caching:
            memcache.set(self.request.uri, resource, self.cacheTime)
            
    def writeToResponse(self, resource):
        self.response.out.write(self.dump(resource))
        self.response.headers["Context-Type"] ="application/json"
        self.setConditional(resource)        
 
    def put(self, args):
        self.setProperty(args);
        
        try:
            putResource = simplejson.load(self.request.body_file)
        except (ValueError, TypeError, IndexError):
            self.response.set_status(400)
            return
            
        # Lookup or create a area, then update it
        resource = self.getResource()
        created = False
        if not resource:
            created = True
            resource = self.newResource()
            
        self.load(resource, putResource)      
        resource.save()
        
        # Return the serialized object, with either a 200 (OK) or a 201
        # (Created) status code.
        self.response.out.write(self.dump(resource))
        self.response.headers["Context-Type"] = "application/json"
        if created:
            self.response.set_status(201)
            self.response.headers["Location"] = self.getUri()

        if self.caching:
            memcache.delete(self.request.uri)     
    
    def delete(self, args):
        self.setProperty(args);
        
        # Look up the area...
        resource = self.getResource()    
        if not resource:
            self.response.set_status(404)
            return

        # ... and delete it.
        self.deleteResource(resource)

        # Return a 204 ("no content")
        self.response.set_status(204)

        if self.caching:
            memcache.delete(self.request.uri)
    
    def getResource(self):
        raise AttributeError
               
    def newResource(self):
        raise AttributeError

    def deleteResource(self, resource):
        raise AttributeError
    
    def getUri(self):
        raise AttributeError
    
    def load(self, obj, putResource):        
        specialLoaders = self.getFieldLoader();
        for field in obj.properties().keys():
            if field in self.hiddenFields:
                continue
            
            if field in putResource :
                newVal = putResource[field]
                if newVal and len(newVal) > 0:
                    if field in specialLoaders:
                        specialLoaders[field](obj, field, newVal)
                    else:    
                        setattr(obj, field, newVal)
    
    def getFieldLoader(self):
        return {}

    def dump(self, obj):
        fields = {}
        specialDumbers = self.getFieldsDumper();
        for field in obj.properties().keys():
            if field in self.hiddenFields:
                continue
            
            if field in specialDumbers:
                fields[field] = specialDumbers[field](obj, field)
            else:    
                fields[field] = getattr(obj, field)
        json = StringIO()
        simplejson.dump(fields, json, ensure_ascii=False)
        if "callback" in self.request.GET:
            return ('%s(%s);' % (self.request.GET['callback'], json.getvalue()))
        else:
            return json.getvalue()

    def getFieldsDumper(self):
        return {}