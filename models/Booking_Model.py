from google.appengine.ext import ndb


class Booking(ndb.Model):
    uuid = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    surname = ndb.StringProperty(required=True)
    start = ndb.DateTimeProperty(auto_now=True)
    stop = ndb.DateTimeProperty(default=None)