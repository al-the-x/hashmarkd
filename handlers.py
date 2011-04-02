from google.appengine.ext import db
from base import RequestHandler
from models import Tweet, User
import functools, tweepy, yaml

def login_optional ( f ):
    @functools.wraps(f)
    def get_user ( self, *args, **kwargs ):
        user = User.for_screen_name(self.request.get('screen_name', None))

        return f(self, user, *args, **kwargs)
    return get_user


class IndexPage ( RequestHandler ):
    def get ( self ):
        self.view.recents = [ ]

        self.render_to_response('index.haml')


class MarkdPage ( RequestHandler ):
    @login_optional
    def get ( self, user ):
        self.view.user = user

        self.view.by_me = Tweet.all_from(
            user.id if user else None
        ).fetch(limit = 5)

        self.view.for_me = Tweet.all_to(
            user.id if user else None
        ).fetch(limit = 5)

        self.render_to_response('markd.haml')


class FetchTask ( RequestHandler ):
    #@db.run_in_transaction
    def get ( self ):
        last_tweet = Tweet.all().get()

        since = last_tweet and last_tweet.created_at

        self.response.out.write(
            'Fetching since "%s":' % since.isoformat() if since else 'Initial run:'
        )

        for result in tweepy.api.search('#markd', filter = 'links', since = since):
            t = Tweet.get_or_insert(result.id_str, status_id = result.id_str,
                from_user = User.for_screen_name(result.from_user),
                to_user = User.for_user_id(result.to_user_id),
                created_at = result.created_at, text = result.text
            )

            self.response.out.write('.' if t else 'X')

        else: self.response.out.write('Done.')


URLS = [
    (r'/', IndexPage),
    (r'/markd/', MarkdPage),
    (r'/tasks/fetch/', FetchTask),
]
