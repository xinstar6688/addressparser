from address.services import AreaParser, AreaImporter, ExcludeWordImporter
from google.appengine.ext import webapp
from wsgiref.handlers import CGIHandler

application = webapp.WSGIApplication([
    (r'/parse', AreaParser),
    (r'/areas', AreaImporter),
    (r'/excludeWords', ExcludeWordImporter)
], debug=True)

def main():
    CGIHandler().run(application)

if __name__ == '__main__':
    main()
