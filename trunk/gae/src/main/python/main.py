from address.services import AreaParser, AreaResource
from google.appengine.ext import webapp
from wsgiref.handlers import CGIHandler

application = webapp.WSGIApplication([
  ('/parse', AreaParser),
  ('/areas/([\w-]+)', AreaResource)
], debug=True)

def main():
    CGIHandler().run(application)

if __name__ == '__main__':
    main()
