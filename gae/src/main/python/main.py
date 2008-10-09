from address.services import AreaParserService, AreasService, \
    ExcludeWordsService, AreaResource, AddressService
from google.appengine.ext import webapp
from wsgiref.handlers import CGIHandler

application = webapp.WSGIApplication([
    (r'/parse', AreaParserService),
    (r'/areas', AreasService),
    (r'/areas/([\w-]+)', AreaResource),
    (r'/excludeWords', ExcludeWordsService),
    (r'/address', AddressService)
], debug=True)

def main():
    CGIHandler().run(application)

if __name__ == '__main__':
    main()
