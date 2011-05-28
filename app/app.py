import sys

sys.path = [ 'lib' ] + sys.path

if __name__ == '__main__':
    import webapp2 as webapp
    from hashmarkd.handlers import URLS

    webapp.WSGIApplication(URLS).run()

