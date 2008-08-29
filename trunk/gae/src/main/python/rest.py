from StringIO import StringIO
from django.http import HttpResponseNotAllowed, HttpResponse, Http404
from django.utils import simplejson

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

    def do_GET(self):
        # Look up the area (possibly throwing a 404)
        resource =  self.getResource()   
        if not resource:
            raise Http404('No Resource matches the given query.')

        return HttpResponse(self.dump(resource), mimetype="application/json")   

    def do_PUT(self):
        # Lookup or create a area, then update it
        resource = self.getResource()
        created = False
        if not resource:
            created = True
            resource = self.newResource()
            
        self.load(resource)      
        resource.save()
        
        # Return the serialized object, with either a 200 (OK) or a 201
        # (Created) status code.
        response = HttpResponse(self.dump(resource), mimetype="application/json")
        if created:
            response.status_code = 201
            response["Location"] = self.getUri()
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
        return response
    
    def getResource(self):
        raise AttributeError
               
    def newResource(self):
        raise AttributeError

    def deleteResource(self, resource):
        raise AttributeError
    
    def getUri(self):
        raise AttributeError
    
    def load(self, obj):        
        try:
            put_area = simplejson.load(StringIO(self.request.raw_post_data))
        except (ValueError, TypeError, IndexError):
            response = HttpResponse()
            response.status_code = 400
            return response
            
        specialLoaders = self.getFieldLoader();
        for field in obj.properties().keys():
            if (put_area.has_key(field)) :
                newVal = put_area[field]
                if newVal and len(newVal) > 0:
                    if specialLoaders.has_key(field):
                        specialLoaders[field](obj, field, newVal)
                    else:    
                        setattr(obj, field, newVal)
    
    def getFieldLoader(self):
        return {}

    def dump(self, obj):
        fields = {}
        specialDumbers = self.getFieldsDumper();
        for field in obj.properties().keys():
            if specialDumbers.has_key(field):
                fields[field] = specialDumbers[field](obj, field)
            else:    
                fields[field] = getattr(obj, field)
        json = StringIO()
        simplejson.dump(fields, json, ensure_ascii=False)
        return json.getvalue()

    def getFieldsDumper(self):
        return {}