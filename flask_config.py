from flask import *
from flask_wtf.csrf import CSRFProtect
from admin.controllers import admin
from main.controllers import main
from auth.controllers import auth
from arduinoHandler.controllers import arduino


app = Flask(__name__)


#app.secret_key = "%xMb^6m%z?Fup3wC(T{9MrhH'|G(ZS"
app.secret_key = "sezdrtfyuijko"
app.register_blueprint(main)
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(arduino, url_prefix='/arduino')
DEFAULT_SENDER = "cla.mar92@gmail.com"

csrf = CSRFProtect(app)
csrf.exempt("arduinoHandler.controllers.addParking")
csrf.exempt("arduinoHandler.controllers.setParking")
csrf.exempt("arduinoHandler.controllers.test_attuatore")

