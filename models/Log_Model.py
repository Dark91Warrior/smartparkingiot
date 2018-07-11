from google.appengine.ext import ndb


class Log(ndb.Model):
    uuid = ndb.StringProperty()
    user_id = ndb.StringProperty()
    timestamp = ndb.DateTimeProperty()
    action = ndb.StringProperty()