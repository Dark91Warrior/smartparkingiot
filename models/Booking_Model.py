from google.appengine.ext import ndb


class Booking(ndb.Model):
    uuid = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    surname = ndb.StringProperty(required=True)
    targa = ndb.StringProperty(required=True)
    start = ndb.DateTimeProperty(default=None)
    stop = ndb.DateTimeProperty(default=None)
    is_taken = ndb.BooleanProperty(default=False)
    parking = ndb.StringProperty(required=True)