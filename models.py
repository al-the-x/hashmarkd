from google.appengine.ext import db
import tweepy

class User ( db.Model ):
    id = db.StringProperty()

    screen_name = db.StringProperty()


    @classmethod
    def for_user_id ( cls, user_id ):
        if not user_id: return None

        try: twitter_user = tweepy.api.get_user(user_id = user_id)

        except tweepy.error.TweepError: return None

        return cls.get_or_insert(twitter_user.screen_name,
            id = twitter_user.id_str, screen_name = twitter_user.screen_name
        )


    @classmethod
    def for_screen_name ( cls, screen_name ):
        if not screen_name: return None

        return cls.get_or_insert(screen_name, **dict( (k, str(v)) for k, v in vars(
            tweepy.api.get_user(screen_name = screen_name)
        ).items() if k in ( 'id', 'screen_name' ) ))


    def __str__ ( self ): return unicode(self)

    def __unicode__ ( self ):
        return unicode(self.screen_name)


class Tweet ( db.Model ):
    status_id = db.StringProperty()

    from_user = db.ReferenceProperty(User,
        collection_name = 'tweets_from'
    )

    to_user = db.ReferenceProperty(User,
        collection_name = 'tweets_to'
    )

    created_at = db.DateTimeProperty()

    text = db.StringProperty(
        multiline = True
    )


    @classmethod
    def all ( cls, *args, **kwargs ):
        return super(Tweet, cls).all(
            *args, **kwargs
        ).order('-created_at')


    @classmethod
    def all_from ( cls, user_id ):
        return cls.all().filter('from_user_id =', user_id)


    @classmethod
    def all_to ( cls, user_id ):
        if not user_id: return cls.all().filter('from_user_id =', None)

        return cls.all().filter('to_user_id =', user_id)


    def __str__ (self ): return self.__unicode__()

    def __unicode__ ( self ):
        return unicode(self.text)


