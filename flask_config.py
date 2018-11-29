from flask import *
from flask_wtf.csrf import CSRFProtect
from admin.controllers import admin
from main.controllers import main
from auth.controllers import auth
from arduinoHandler.controllers import arduino


app = Flask(__name__)

CSRFProtect(app)

#app.secret_key = "%xMb^6m%z?Fup3wC(T{9MrhH'|G(ZS"
app.secret_key = "sezdrtfyuijko"
app.register_blueprint(main)
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(arduino, url_prefix='/arduino')
DEFAULT_SENDER = "cla.mar92@gmail.com"