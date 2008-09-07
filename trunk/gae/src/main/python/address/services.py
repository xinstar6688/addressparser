# -*- coding: utf-8 -*-

from address.models import AreaParser, Area, ExcludeWord
from django.utils import simplejson
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import RequestHandler
from sgmllib import SGMLParser
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
        
        normalizedAddresses = AddressNormalizer.normalize(address)
        if len(normalizedAddresses) == 0:
            normalizedAddresses = [address]
        areas = []
        for normalizedAddress in normalizedAddresses:
            areas.extend(AreaParser.parse(normalizedAddress)) 
        
        logging.info("got areas[%s] for %s" % (",".join([area.name for area in areas]), address))

        body = '{"areas":[%s]}' % ",".join([area.toJson() for area in areas])
        callback = self.request.get("callback", None)
        if callback:
            body = ('%s(%s);' % (callback, body))
        self.response.out.write(body);
        self.response.headers["Content-type"] = "application/json"
    
class AddressNormalizer:
    _url = "http://ditu.google.cn/maps?output=js&q="
    
    @classmethod
    def normalize(cls, address):
        result = urlfetch.fetch(cls._url + unicode(address))
        if result.status_code == 200:
            charset = result.headers["Content-Type"].partition("charset=")[2]
            if charset.lower() == "gb2312" : charset = "gbk"
            content = result.content.decode(charset)
            content = content.partition('panel:"')[2].partition('",panelStyle:')[0]
            content = content.replace(r"\x3c", "<")
            content = content.replace(r"\x3e", ">")
            content = content.replace(r"\x26", "&")
            content = content.replace(r'\ "', '"')
            content = content.replace(r'\"', '"')
            
            parser = AddressHTMLProcessor()
            parser.feed(content)
            parser.close()
            return parser.found
        
class AddressHTMLProcessor(SGMLParser):
    _find = False;
    found = []

    def reset(self):
        self.found = []
        SGMLParser.reset(self)
        
    def start_div(self, attrs):
        for attr in attrs:
            if (attr[0] == "class" and attr[1] in ("ref_desc", "adr")):
                self._find = True
                
    def handle_data(self, text):
        if self._find:
            self.found.append(text)
            
    def end_div(self):
        self._find = False
        
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
                if field == "alias":
                    setattr(area, field, newVal.split())
                else:
                    setattr(area, field, newVal)
        area.put()
        
        if created:
            logging.info("area[%s] is created " % code)
            self.response.set_status(201)           
            self.response.headers["Location"] = str("/areas/%s" % code)
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
            ExcludeWord(word=word).put()
        logging.info("exclude words[%s] are put" % ",".join(words))
            
        self.response.set_status(204)
    
    def post(self):
        try:
            word = simplejson.load(self.request.body_file)["word"] 
        except (ValueError, TypeError, IndexError):
            self.response.set_status(400)
            return
        
        logging.info("posting exclude word[%s]" % word)
        ExcludeWord(word=word).put()
        logging.info("exclude word[%s] is post" % word)

        self.response.set_status(204)
        