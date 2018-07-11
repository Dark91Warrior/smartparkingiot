from google.appengine.ext import ndb
from flask_login import UserMixin


class User(UserMixin, ndb.Model):
    uuid = ndb.StringProperty(required=True)
    nome = ndb.StringProperty()
    cognome = ndb.StringProperty()
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    has_superuser = ndb.BooleanProperty(default=False)
    is_valid = ndb.BooleanProperty(default=False)