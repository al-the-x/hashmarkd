from google.appengine.ext import webapp
import haml, mako.lookup

lookup = mako.lookup.TemplateLookup('templates',
    preprocessor = haml.preprocessor
)


class RequestHandler ( webapp.RequestHandler ):
    def render ( self, template, write = True ):
        output = lookup.get_template(template).render()

        if write: self.response.out.write(output)

        return output


class IndexPage ( RequestHandler ):
    def get ( self ):
        self.render('index.haml')


URLS = [
    (r'/', IndexPage),
]
