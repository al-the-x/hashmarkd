from base import Config
from models import Tweet
from datetime import datetime
from handlers import URLS

class JSON(Config):
    def __init__(self, d):
        for k,v in d.items():
            if k.endswith('_at'):
                d[k] = datetime.strptime(v, '%Y-%m-%d %H:%M:%S')

        super(JSON, self).__init__(d)

class DataHandler(RequestHandler):
    def post(self):
        import json
        for tweet in json.loads(self.request.body, object_hook=JSON):
            Tweet.from_tweet(tweet)
            print Tweet



URLS.append(
    (r'/load', DataHandler),
)
