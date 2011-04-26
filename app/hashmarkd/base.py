from google.appengine.ext import webapp
import decorator, haml, mako.lookup, yaml

lookup = mako.lookup.TemplateLookup('templates',
    preprocessor = haml.preprocessor
)

@decorator.decorator
def memoize ( f, *args, **kwargs ):
    'Cache the calculated value and return that on subsequent calls.'
    if not hasattr(f, 'memo'):
        setattr(f, 'memo', f(*args, **kwargs))

    return getattr(f, 'memo')


class config ( dict ):
    '''
    Instead of raising a "KeyError" when a key is missing "config" instances pass
    an empty "config" instance, i.e.
    >>> a = config({ 'foo' : 'bar' })
    >>> a['bar']
    { }
    >>> a['bar'].__class__.__name__
    'config'

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
    >>> a.foo.baz.bat
    { }
    '''

    def __missing__ ( self, name ): return config()

    def __getattr__ ( self, name ): return self[name]

    def __setattr__ ( self, name, value ):
        self[name] = value

        return value


    def __getitem__ ( self, name ):
        item = super(config, self).__getitem__(name)

        return item if (
            not isinstance(item, dict) or isinstance(item, config)
        ) else config(item)


    @classmethod
    def from_yaml ( cls, filename ):
        return cls(yaml.load(open(filename)))


twitter = config.from_yaml('config/twitter.yaml')

google = config.from_yaml('config/google.yaml')


class RequestHandler ( webapp.RequestHandler ):
    view = config()

    urls = config(
        at_anywhere = twitter.at_anywhere.url % twitter.at_anywhere.api_key or None,
        ## FIXME: When we know why "google.load()" isn't working... :/
        #google_loader = google.loader.url % google.loader[hostname].api_key or None,
        jquery = 'http://ajax.googleapis.com/ajax/libs/jquery/1.5.2/jquery.min.js',
    )


    def get_rendered_template ( self, template ):
        return lookup.get_template(template).render(
            view = self.view, urls = self.urls,
        )


    def render_to_response ( self, template ):
        self.response.out.write(self.get_rendered_template(template))

        return self


