# -*- coding: utf-8 -*-

from address.models import AreaParser, Area, ExcludeWord
from django.utils import simplejson
from google.appengine.ext.webapp import RequestHandler
import logging

class AreaResource(RequestHandler):
    def get(self, code):
        logging.info("getting area[%s]" % code)
        area = Area.getByCode(code)
        if area:
            logging.info("got area[%s]" % code)
            self.response.out.write(area.toJson());
            self.response.headers["Content-type"] = "application/json"
        else:
            logging.info("area[%s] not found" % code)
            self.response.set_status(404)

class AreaParserService(RequestHandler):
    def get(self):
        address = self.request.get("q")
        logging.info("parsing %s" % address)
        
        areas = AreaParser.parse(address)
        logging.info("got areas[%s] for %s" % (",".join([area.name for area in areas]), address))

        body = '{"areas":[%s]}' % ",".join([area.toJson() for area in areas])
        self.response.out.write(body);
        self.response.headers["Content-type"] = "application/json"
        
class AreasService(RequestHandler):
    def post(self):
        try:
            putArea = simplejson.load(self.request.body_file) 
        except (ValueError, TypeError, IndexError):
            self.response.set_status(400)
            return
        
        code = putArea["code"]
        logging.info("posting area[%s]" % code)
        
        area = Area.getByCode(putArea["code"])
        (area, created) = area and (area, False) or (Area(), True)
            
        for field in area.properties().keys():
            newVal = putArea.get(field, None)
            if newVal:
                setattr(area, field, newVal)
        area.save()
        
        if created:
            logging.info("area[%s] is created " % code)
            self.response.set_status(201)           
            self.response.headers["Location"] = "/areas/%s" % code
        else:
            logging.info("area[%s] is modified" % code)
            self.response.set_status(204)
        
    def delete(self):
        logging.info("clearing all areas")
        Area.clear()
        
        logging.info("all areas are cleared")
        self.response.set_status(204)
        
class ExcludeWordsService(RequestHandler):
    def put(self):
        try:
            words = simplejson.load(self.request.body_file)["words"] 
        except (ValueError, TypeError, IndexError):
            self.response.set_status(400)
            return
        
        logging.info("putting exclude words[%s]" % ",".join(words))
        ExcludeWord.clear()
        logging.info("exclude words are cleared")
        
        for word in words:
            ExcludeWord(word = word).save()
        logging.info("exclude words[%s] are put" % ",".join(words))
            
        self.response.set_status(204)
    
    def post(self):
        try:
            word = simplejson.load(self.request.body_file)["word"] 
        except (ValueError, TypeError, IndexError):
            self.response.set_status(400)
            return
        
        logging.info("posting exclude word[%s]" % word)
        ExcludeWord(word = word).save()
        logging.info("exclude word[%s] is post" % word)

        self.response.set_status(204)
        