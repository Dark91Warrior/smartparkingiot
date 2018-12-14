from google.appengine.ext import ndb

"""
Model per le prenotazione real-time.
"""

class Booking(ndb.Model):
    uuid = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    surname = ndb.StringProperty(required=True)
    targa = ndb.StringProperty(required=True)
    start = ndb.DateTimeProperty(default=None)
    stop = ndb.DateTimeProperty(default=None)
    parking = ndb.StringProperty(required=True)
    costo = ndb.FloatProperty(default=None)