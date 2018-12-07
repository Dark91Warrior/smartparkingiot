from google.appengine.ext import ndb

class Tariffa(ndb.Model):
    tariffa = ndb.StringProperty()
    order = ndb.IntegerProperty(required=True)
    description = ndb.StringProperty()
    prezzo = ndb.FloatProperty()
    visibilita = ndb.BooleanProperty(default=True)
