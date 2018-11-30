from google.appengine.ext import ndb

class Tariffa(ndb.Model):
    tariffa = ndb.StringProperty()
    order = ndb.IntegerProperty()
    description = ndb.StringProperty()
    prezzo = ndb.FloatProperty()
