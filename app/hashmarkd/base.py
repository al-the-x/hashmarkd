import webapp2 as webapp
import decorator, haml, mako.lookup, yaml

lookup = mako.lookup.TemplateLookup('templates',
    preprocessor = haml.preprocessor
)

class Config(dict):
    '''
    Instead of raising a "KeyError" when a key is missing "config" instances pass
    an empty "config" instance, i.e.
    >>> a = Config({ 'foo' : 'bar' })
    >>> a['bar']
    { }
    >>> a['bar'].__class__.__name__
    'Config'

    They also allow either subscript or attribute notation to access the contents
    as it's a little easier on the eyes:
    >>> a['foo'] == a.foo
    True
    >>> a.bar = 'baz'
    >>> a.bar == a[a.foo]
    True

    And any "dict" (or subclassed) values are converted into "config" type on the
    way out, to allow for chaining:
    >>> a.foo = { 'bar' : 'baz' }
    >>> a.foo
    { 'bar' : 'baz' }
    >>> a.foo.bar
    'baz'
    >>> a.foo.baz
    { }
    >>> a.foo.baz
    { }
    >>> a.foo.baz.bat
    { }
    '''

    def __init__(self, *args, **kwargs):
        super(Config, self).__init__()

        args +=(kwargs, )

        for arg in args:
            self.update(arg)


    def __missing__(self, name):
        return Config()

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

        return value


    def __getitem__(self, name):
        item = super(Config, self).__getitem__(name)

        return item if (
            not isinstance(item, dict) or isinstance(item, Config)
        ) else Config(item)


    def __add__(self, other):
        return Config(self, other)

    def __call__(self, *args, **kwargs):
        return None


    @classmethod
    def from_yaml(cls, filename):
        return cls(yaml.load(open(filename)))


class RequestHandler(webapp.RequestHandler):
    config = Config(
        twitter={
            'urls': Config.from_yaml('twitter.yaml'),
            'oauth': Config.from_yaml('oauth.yaml'),
        }
    )

    view = Config(
        urls = dict(
            twitter = config.twitter.urls,
            ## FIXME: When we know why "google.load()" isn't working... :/
            #google_loader = google.loader.url % google.loader[hostname].api_key or None,
            jquery = 'http://ajax.googleapis.com/ajax/libs/jquery/1.5.2/jquery.min.js',
        )
    )


    def __init__(self, *args, **kwargs):
        self.view = RequestHandler.view if not self.view else (
            RequestHandler.view + self.view
        )

        super(RequestHandler, self).__init__(*args, **kwargs)



    def get_rendered_template(self, template):
        return lookup.get_template(template).render(
            v = self.view
        )


    def render_to_response(self, template):
        self.response.out.write(self.get_rendered_template(template))

        return self


