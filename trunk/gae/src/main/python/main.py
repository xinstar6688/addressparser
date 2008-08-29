import logging, os
from google.appengine.ext.webapp import util

# Force Django to reload its settings.
from django.conf import settings
settings._target = None

# Must set this env var before importing any part of Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.dispatch import dispatcher
from django.core.handlers.wsgi import WSGIHandler
from django.core.signals import got_request_exception
from django.db import _rollback_on_exception

def log_exception(*args, **kwds):
    logging.exception('Exception in request:')

# Log errors.
dispatcher.connect(
   log_exception, got_request_exception)

# Unregister the rollback event handler.
dispatcher.disconnect(
    _rollback_on_exception, got_request_exception)

def main():
    # Create a Django application for WSGI.
    application = WSGIHandler()
    
    # Run the WSGI CGI handler with that application.
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()