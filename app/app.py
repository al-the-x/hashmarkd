from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import sys

sys.path = [ 'lib' ] + sys.path


if __name__ == '__main__':
    from hashmarkd.handlers import URLS

    run_wsgi_app(webapp.WSGIApplication(
        URLS, debug = True
    ))

