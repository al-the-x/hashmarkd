from google.appengine.ext import db
from base import RequestHandler
from models import Tweet, User
import decorator, tweepy, yaml

@decorator.decorator
def add_user_to_request ( f, self, *args, **kwargs ):
    '''
    Pull the "screen_name" parameter and display Tweets for that User,
    if we have any. This is all public data anyway, so we're not concerned
    about authentication yet.
    '''

    self.request.user = User.for_screen_name(
        self.request.get('screen_name', None)
    )

    return f(self, *args, **kwargs)


class IndexPage ( RequestHandler ):
    @add_user_to_request
    def get ( self ):
        user = self.request.user

        self.view.user = user

        self.view.by_me = Tweet.all_from(
            user.id if user else None
        ).fetch(limit = 5)

        self.view.for_me = Tweet.all_to(
            user.id if user else None
        ).fetch(limit = 5)

        self.render_to_response('index.haml')


class FetchTask ( RequestHandler ):
    #@db.run_in_transaction
    def get ( self ):
        last_tweet = Tweet.all().get()

        since = last_tweet and last_tweet.created_at

        self.response.out.write(
            'Fetching since "%s":' % since.isoformat() if since else 'Initial run:'
        )

        for result in tweepy.api.search('#markd', filter = 'links', since = since):
            ## TODO: Refactor into class method of Tweet
            t = Tweet.get_or_insert(result.id_str, status_id = result.id_str,
                from_user = User.for_screen_name(result.from_user),
                to_user = User.for_user_id(result.to_user_id),
                created_at = result.created_at, text = result.text
            )

            ## Just some sanity checks to let me know you're workin', buddy...
            self.response.out.write('.' if t else 'X')

        self.response.out.write('Done.')


URLS = [
    (r'/', IndexPage),
    (r'/tasks/fetch/', FetchTask),
]
