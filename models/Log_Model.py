from google.appengine.ext import ndb

"""
Model per i Log d'accesso.
"""

class Log(ndb.Model):
    uuid = ndb.StringProperty()
    user_id = ndb.StringProperty()
    timestamp = ndb.DateTimeProperty()
    action = ndb.StringProperty()