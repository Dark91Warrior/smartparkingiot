from common.commons import get_username
from flask import *
from auth.forms import UserInfoModify, UserPwdChange
from data_access import DataAccess as DA


main = Blueprint('main', __name__)


@main.before_request
def before_request():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    elif session['user']['active'] == False:
        return redirect(url_for('auth.login'))
    elif session['user']['authenticated'] == False:
        return redirect(url_for('auth.login'))


@main.route('/')
def index():
    return render_template('base.html', username=get_username(session), is_admin=session['user']['superuser'])
