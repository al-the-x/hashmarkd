import webapp2 as webapp
from base import RequestHandler
from models import Tweet, User
import decorator, logging, tweepy

@decorator.decorator
def add_user_to_request ( f, self, screen_name, *args, **kwargs ):
    '''
    Pull the "screen_name" parameter and display Tweets for that User,
    if we have any. This is all public data anyway, so we're not concerned
    about authentication yet.
    '''

    self.request.user = User.for_screen_name(
        screen_name or self.request.get('screen_name') or 'hashmarkd'
    )

    if not self.request.user:
        ## self.flash('Not a valid user account...')
        self.request.user = User.for_screen_name('hashmarkd')

    return f(self, screen_name, *args, **kwargs)


@decorator.decorator
def add_pagination ( f, self, screen_name, page, count, *args, **kwargs ):
    page = page or 1; count = count or 10

    return f(self, screen_name, page, count, *args, **kwargs)


class IndexPage ( RequestHandler ):
    @add_user_to_request
    def get ( self, screen_name = None ):
        user = self.view.user = self.request.user

        self.view.by_me = user.tweets_from.fetch(limit = 10)

        self.view.for_me = user.tweets_to.fetch(limit = 10)

        self.render_to_response('index.haml')


class TweetsPage ( RequestHandler ):
    def tweets ( self, user ): pass


    @add_user_to_request
    @add_pagination
    def get ( self, screen_name, page, count ):
        self.view.user = self.request.user

        self.view.tweets = self.tweets(self.request.user).fetch(
            limit = count, offset = count * (page - 1)
        )

        self.render_to_response('tweets.haml')


class MarkedByPage ( TweetsPage ):
    view = dict(name = 'by_me')

    def tweets ( self, user ):
        return user.tweets_from


class MarkedForPage ( RequestHandler ):
    name = 'for_me'

    def tweets ( self, user ):
        return user.tweets_to


class FetchTask ( RequestHandler ):
    def get ( self ):
        self.response.out.write('Fetching new tweets: ')

        ## Keep GAE from retrying if rate-limited by Twitter...
        try: results = tweepy.api.search('#markd', filter = 'links')

        except tweepy.TweepError, error:
            logging.warning(error)

            self.response.out.write(error)

            return

        for result in results:
            try:
                ## TODO: Refactor into class method of Tweet
                Tweet.get_or_insert(result.id_str, status_id = result.id_str,
                    from_user = User.get_or_insert(result.from_user,
                        id = result.from_user_id_str, screen_name = result.from_user,
                    ),
                    to_user = User.for_user_id(result.to_user_id),
                    created_at = result.created_at, text = result.text
                )

                self.response.out.write('.')

            ## In case that "User.for_user_id" call fails, ignore this "result" for now...
            except tweepy.TweepError, error:
                logging.warning(error)

                self.response.out.write('X')


URLS = [
    (r'/(\w+)?/?', IndexPage),
    (r'/markd_by/(\w+)/(?:page/(\d+)/)?(?:count/(\d+)/)?', MarkedByPage),
    (r'/markd_for/(\w+)/(?:page/(\d+)/)?(?:count/(\d+)/)?', MarkedForPage),
    (r'/tasks/fetch/?', FetchTask),
]
