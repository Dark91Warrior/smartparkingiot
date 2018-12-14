from flask import *
from flask_wtf.csrf import CSRFProtect
from admin.controllers import admin
from main.controllers import main
from auth.controllers import auth
from arduinoHandler.controllers import arduino

"""
Gestione dei BluePrint
"""

app = Flask(__name__)

app.secret_key = "sezdrtfyuijko"

# utenti
app.register_blueprint(main)

# amministratori
app.register_blueprint(admin, url_prefix='/admin')

# sezione login
app.register_blueprint(auth, url_prefix='/auth')

# comunicazione arduino
app.register_blueprint(arduino, url_prefix='/arduino')

# email mittente
DEFAULT_SENDER = "cla.mar92@gmail.com"

# protezione con token
csrf = CSRFProtect(app)

# esenzione da protezione token, per comunicazione con arduino
csrf.exempt("arduinoHandler.controllers.addParking")
csrf.exempt("arduinoHandler.controllers.setParking")
csrf.exempt("arduinoHandler.controllers.test_attuatore")
csrf.exempt("arduinoHandler.controllers.attesa")

