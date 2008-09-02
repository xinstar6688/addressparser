from address.services import AreaParser, AreaResource, ExcludeWordImporter
from google.appengine.ext import webapp
from wsgiref.handlers import CGIHandler

application = webapp.WSGIApplication([
    (r'/parse', AreaParser),
    (r'/areas/([\w-]+)', AreaResource),
    (r'/excludeWords', ExcludeWordImporter)
], debug=True)

def main():
    CGIHandler().run(application)

if __name__ == '__main__':
    main()
