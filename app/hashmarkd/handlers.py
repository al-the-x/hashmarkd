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

HTML = 'html'
RSS = 'rss'

class IndexPage ( RequestHandler ):
    @add_user_to_request
    def get ( self, screen_name = None, fmt = HTML ):
        user = self.view.user = self.request.user

        self.view.by_me = user.tweets_from

        self.view.for_me = user.tweets_to

        self.render_to_response('index.haml')


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
    (r'/tasks/fetch/?', FetchTask),
]
