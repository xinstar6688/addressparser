from StringIO import StringIO
from address.models import Area
from django.http import HttpResponse, Http404
from django.utils import simplejson
from rest import Resource

class AreaDetail(Resource):
    def setProperty(self, areaCode):
        self.areaCode = areaCode
    
    def do_GET(self):
        # Look up the area (possibly throwing a 404)
        area = Area.getByCode(self.areaCode)     
        if not area:
            raise Http404('No %s matches the given query.' % "Area")

        return HttpResponse(self.dump(area), mimetype="application/json")
    
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
                if new_val and len(new_val) > 0:
                    setattr(area, field, new_val)
                
        new_val = put_area["parentArea"]
        if new_val and len(new_val) > 0:
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
            
    def dump(self, obj):
        fields = {}
        for field in obj.properties().keys():
            if field == "parentArea" :
                parentArea = getattr(obj, field);
                if parentArea:
                    fields[field] = parentArea.code
            else:    
                fields[field] = getattr(obj, field)
        json = StringIO()
        simplejson.dump(fields, json, ensure_ascii=False)
        return json.getvalue()
    
    def load(self, str):
        return simplejson.load(StringIO(str))
