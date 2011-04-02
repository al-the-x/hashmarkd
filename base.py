from google.appengine.ext import webapp
import haml, mako.lookup, yaml

lookup = mako.lookup.TemplateLookup('templates',
    preprocessor = haml.preprocessor
)

twitter = yaml.load(open('twitter.yaml', 'r'))


class view ( dict ):
    def __missing__ ( self, name ):
        return None


    def __getattr__ ( self, name ):
        return self[name]


    def __setattr__ ( self, name, value ):
        self[name] = value

        return value


class RequestHandler ( webapp.RequestHandler ):
    segments = { }

    view = view(at_anywhere_url = (
        twitter['at_anywhere']['url'] % twitter['at_anywhere']['api_key']
    ))


    def get_rendered_template ( self, template ):
        return lookup.get_template(template).render(
            segments = self.segments,
            view = self.view
        )


    def render_to_response ( self, template ):
        self.response.out.write(self.get_rendered_template(template))

        return self


    def render_to_segment ( self, template, segment = 'default' ):
        self.segments[segment] = self.get_rendered_template(template)

        return self


