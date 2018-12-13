from google.appengine.ext import ndb

class Test(ndb.Model):
    parking = ndb.StringProperty(required=True)
    last_data = ndb.DateTimeProperty(auto_now=True)
