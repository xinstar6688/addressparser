from address.models import Area
from django.core import serializers
from django.http import HttpResponseNotAllowed, HttpResponse, Http404

class AreaDetail:
    def __call__(self, request, areaCode):
        self.request = request
        self.areaCode = areaCode
        
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
    
    def do_GET(self):
        # Look up the area (possibly throwing a 404)
        area = Area.getByCode(self.areaCode)     
        if not area:
            raise Http404('No %s matches the given query.' % "Area")


        json = serializers.serialize("json", [area])
        return HttpResponse(json, mimetype="application/json")
            
    def do_PUT(self):
        # Deserialize the object from the request. Serializers work the lists,
        # but we're only expecting one here. Any errors and we return a 400.
        try:
            deserialized = serializers.deserialize("json", self.request.raw_post_data)
            put_area = list(deserialized)[0].object
        except (ValueError, TypeError, IndexError):
            response = HttpResponse()
            response.status_code = 400
            return response
            
        # Lookup or create a area, then update it
        area = Area.getByCode(self.areaCode)
        if not area:
            created = True
            area = Area(self.areaCode)
            
        for field in ["name", "middle", "unit"]:
            new_val = getattr(put_area, field, None)
            if new_val:
                setattr(area, field, new_val)
                
        new_val = getattr(put_area, "parentArea", None)
        if new_val:
            parentArea = Area.getByCode(new_val)
            setattr(area, "parentArea", parentArea)  
              
        area.save()
        
        # Return the serialized object, with either a 200 (OK) or a 201
        # (Created) status code.
        json = serializers.serialize("json", [area])
        response = HttpResponse(json, mimetype="application/json")
        if created:
            response.status_code = 201
            response["Location"] = "/areas/%s" % (area.code)
        return response
        
    def do_DELETE(self):
        # Look up the area...
        area = Area.getByCode(self.areaCode)     
        if not area:
            raise Http404('No %s matches the given query.' % "Area")

        # ... and delete it.
        area.delete()

        # Return a 204 ("no content")
        response = HttpResponse()
        response.status_code = 204
        return response
