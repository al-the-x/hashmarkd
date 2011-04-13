from google.appengine.ext import db
import tweepy

class User ( db.Model ):
    id = db.StringProperty()

    screen_name = db.StringProperty()


    @classmethod
    def get_or_insert_for ( cls, **kwargs ):
        try: user = tweepy.api.get_user(**kwargs)

        except tweepy.TweepError: return None

        return cls.get_or_insert(user.screen_name,
            id = user.id_str, screen_name = user.screen_name
        )


    @classmethod
    def for_user_id ( cls, user_id ):
        return (
            cls.all().filter('user_id =', user_id).get() or
            cls.get_or_insert_for(id = user_id)
        )


    @classmethod
    def for_screen_name ( cls, screen_name ):
        return (
            cls.all().filter('screen_name =', screen_name).get() or
            cls.get_or_insert_for(screen_name = screen_name)
        )


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


    def __str__ (self ): return self.__unicode__()

    def __unicode__ ( self ):
        return unicode(self.text)


