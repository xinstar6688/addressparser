from StringIO import StringIO
from address.models import Area
from django.http import HttpResponseNotAllowed, HttpResponse, Http404
from django.utils import simplejson

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

        return HttpResponse(self.dump(area), mimetype="application/json")
            
    def dump(self, obj):
        fields = {}
        for field in obj._meta.fields:
            if field.name == "parentArea" :
                parentArea = getattr(obj, field.name);
                if parentArea:
                    fields[field.name] = parentArea.code
            else:    
                fields[field.name] = getattr(obj, field.name)
        json = StringIO()
        simplejson.dump(fields, json, ensure_ascii=False)
        return json.getvalue()
    
    def load(self, str):
        return simplejson.load(StringIO(str))
    
    def do_PUT(self):
        # Deserialize the object from the request. Serializers work the lists,
        # but we're only expecting one here. Any errors and we return a 400.
        try:
            put_area = self.load(self.request.raw_post_data)
        except (ValueError, TypeError, IndexError):
            response = HttpResponse()
            response.status_code = 400
            return response
            
        # Lookup or create a area, then update it
        area = Area.getByCode(self.areaCode)
        created = False
        if not area:
            created = True
            area = Area(code = self.areaCode)
            
        for field in ["name", "middle", "unit"]:
            if (put_area.has_key(field)) :
                new_val = put_area[field]
                if len(new_val) > 0:
                    setattr(area, field, new_val)
                
        new_val = put_area["parentArea"]
        if len(new_val) > 0:
            parentArea = Area.getByCode(new_val)
            setattr(area, "parentArea", parentArea)  
              
        area.save()
        
        # Return the serialized object, with either a 200 (OK) or a 201
        # (Created) status code.
        response = HttpResponse(self.dump(area), mimetype="application/json")
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
