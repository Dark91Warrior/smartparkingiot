from data_access import DataAccess as DA
from flask import *

admin = Blueprint('admin', __name__)


@admin.before_request
def before_request():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    elif session['user']['active'] == False:
        return redirect(url_for('auth.login'))
    elif session['user']['authenticated'] == False:
        return redirect(url_for('auth.login'))
    elif session['user']['authenticated'] == True and session['user']['superuser'] == False:
        return redirect(url_for('auth.login'))


#---------- items -----------#



#---------- users -----------#


@admin.route('/del_user', methods=['POST'])
def del_user():
    if request.method == 'POST':
        msg_del = DA.delete_user(request.form['del_user'])
        flash(msg_del)
        return redirect(request.referrer)