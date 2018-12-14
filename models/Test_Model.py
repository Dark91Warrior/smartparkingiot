from google.appengine.ext import ndb

"""
Model per i test dei sensori.
"""

class Test(ndb.Model):
    parking = ndb.StringProperty(required=True)
    last_data = ndb.DateTimeProperty(auto_now=True)
