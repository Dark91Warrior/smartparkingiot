from google.appengine.ext import ndb

"""
Model per la lista dei parcheggi.
"""

class Parking(ndb.Model):
    piano = ndb.StringProperty()
    number = ndb.IntegerProperty()
    stato = ndb.StringProperty(default=None)