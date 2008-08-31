from StringIO import StringIO
from django.http import HttpResponseNotAllowed, HttpResponse, Http404
from django.utils import simplejson
from google.appengine.api import memcache

class Resource:
    def __call__(self, request, args):
        self.request = request
        self.setProperty(args)
        # Try to locate a handler method.
        try:
            callback = getattr(self, "do_%s" % request.method)
        except AttributeError:
            # This class doesn't implement this HTTP method, so return a
            # 405 (method not allowed) response with the allowed methods.
            allowed_methods = [m[3:] for m in dir(self) if m.startswith("do_")]
            return HttpResponseNotAllowed(allowed_methods)
        
        # Call the looked-up method
        return callback()
    
    def setProperty(self, *args):
        pass
    
    def isUnmodified(self, response):
        etag = self.request.META.get("ETAG", None)
        if etag and etag == response.headers.get("ETag", None):
            return True
        lastModified = self.request.META.get("Last-Modified", None)
        if lastModified and lastModified == response.headers.get("Last-Modified", None):
            return True
        return False
    
    lastModifiedField = "lastModified"
    eTagField = "eTag"
    hiddenFields = (lastModifiedField, eTagField)
    def setConditional(self, response, resource):
        lastModified = getattr(resource, self.lastModifiedField, None)
        if lastModified:
            response.headers["Last-Modified"] = lastModified.strftime("%a, %d %b %Y %H:%M:%S GMT")           
        eTag = getattr(resource, self.eTagField, None)
        if eTag:
            response.headers["ETag"] = eTag      

    caching = True
    cacheTime = 300
    def do_GET(self):
        if self.caching:
            response = memcache.get(self.request.path)
            if response:
                if self.isUnmodified(response):
                    response = HttpResponse()
                    response.status_code = 304
                return response

        # Look up the area (possibly throwing a 404)
        resource =  self.getResource()   
        if not resource:
            raise Http404('No Resource matches the given query.')

        response = HttpResponse(self.dump(resource), mimetype="application/json")
        self.setConditional(response, resource)
        
        if self.caching:
            memcache.set(self.request.path, response, self.cacheTime)
        return response

    def do_PUT(self):
        try:
            putResource = simplejson.load(StringIO(self.request.raw_post_data))
        except (ValueError, TypeError, IndexError):
            response = HttpResponse()
            response.status_code = 400
            return response
            
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
        response = HttpResponse(self.dump(resource), mimetype="application/json")
        if created:
            response.status_code = 201
            response["Location"] = self.getUri()

        if self.caching:
            memcache.delete(self.request.path)
        return response       
    
    def do_DELETE(self):
        # Look up the area...
        resource = self.getResource()    
        if not resource:
            raise Http404('No Resource matches the given query.')

        # ... and delete it.
        self.deleteResource(resource)

        # Return a 204 ("no content")
        response = HttpResponse()
        response.status_code = 204

        if self.caching:
            memcache.delete(self.request.path)
            
        return response
    
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