from google.appengine.ext import ndb


class Parking(ndb.Model):
    piano = ndb.StringProperty()
    number = ndb.IntegerProperty()
    stato = ndb.StringProperty(default=None)