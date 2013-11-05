import webapp2 as webapp
from base import RequestHandler
from models import Tweet, User
import decorator, logging, tweepy

@decorator.decorator
def add_user_to_request(f, self, *args, **kwargs):
    '''
    Pull the "screen_name" parameter and display Tweets for that User,
    if we have any. This is all public data anyway, so we're not concerned
    about authentication yet.
    '''

    screen_name = self.view.screen_name = self.request.get('screen_name') or 'hashmarkd'
    ## If no screen_name given, use "hashmarkd"

    self.request.user = User.for_screen_name(screen_name) or User.get_or_insert(
        screen_name, screen_name=screen_name)

    return f(self, *args, **kwargs)


@decorator.decorator
def add_pagination(f, self, screen_name, page, count, *args, **kwargs):
    page=page or 1; count=count or 10

    return f(self, screen_name, page, count, *args, **kwargs)


class IndexPage(RequestHandler):
    @add_user_to_request
    def get(self):
        user = self.view.user = self.request.user

        self.view.by_me = user.tweets_from.order('-created_at')

        self.view.for_me = user.tweets_to.order('-created_at')

        self.render_to_response('index.haml')


class TweetsPage(RequestHandler):
    def tweets(self, user):
        pass

    @add_user_to_request
    @add_pagination
    def get(self, screen_name, page, count):
        self.view.user=self.request.user

        self.view.tweets=self.tweets(self.request.user).fetch(
            limit=count, offset=count * (page - 1)
        )

        self.render_to_response('tweets.haml')


class MarkedByPage(TweetsPage):
    view=dict(name='by_me')

    def tweets(self, user):
        return user.tweets_from


class MarkedForPage(RequestHandler):
    name='for_me'

    def tweets(self, user):
        return user.tweets_to


class FetchTask(RequestHandler):
    def get(self):
        self.response.out.write('Fetching new tweets: ')

        ## Keep GAE from retrying if rate-limited by Twitter...
        try:
            results=tweepy.api.search('#markd', filter='links')

        except tweepy.TweepError as error:
            logging.warning(error)

            self.response.out.write(error)

            return

        for result in results:
            try:
                ## TODO: Refactor into class method of Tweet
                Tweet.from_tweet(result)

                self.response.out.write('.')

            ## In case that "User.for_user_id" call fails, ignore this "result" for now...
            except tweepy.TweepError as error:
                logging.warning(error)

                self.response.out.write('X')


URLS=[
    (r'/', IndexPage),
    (r'/markd_by/(\w+)/(?:page/(\d+)/)?(?:count/(\d+)/)?', MarkedByPage),
    (r'/markd_for/(\w+)/(?:page/(\d+)/)?(?:count/(\d+)/)?', MarkedForPage),
    (r'/tasks/fetch/?', FetchTask),
]
