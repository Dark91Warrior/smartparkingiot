from common.commons import get_username
from flask import *
from main.forms import AddPlate
from models.User_Model import User
from models.Tariffe_Model import Tariffa
from data_access import DataAccess as DA

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

# gestione menu
@admin.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        flash("Utente Amministratore")
        return render_template('base.html', username=get_username(session), is_admin=session['user']['superuser'])
    elif request.method == 'POST':
        command = request.form['command']
        if command == "PARKING":
            return render_template('parking.html', username=get_username(session), is_admin=session['user']['superuser'])
        elif command == "PAGA":
            return render_template('paga.html', username=get_username(session), is_admin=session['user']['superuser'])
        elif command == "TARIFFE":
            tariffe = Tariffa.query().fetch()
            if len(tariffe) > 0:
                return render_template('tariffe_admin.html', len=len(tariffe),
                                       nomi_tariffe=[tar.tariffa for tar in tariffe],
                                       descr_tariffe=[tar.description for tar in tariffe])
            else:
                return render_template('tariffe_admin.html', len=1,
                                       nomi_tariffe=["Non ci sono tariffe."],
                                       descr_tariffe=["Tutti gratis, paliazzu!!"])
        if command == "PROFILO":
            form = AddPlate(request.form)
            user = User().query(User.email == session['user']['email']).fetch(1)[0]
            targhe = user.targa.split(",")
            return render_template('profilo.html', username=get_username(session), is_admin=session['user']['superuser'], form=form, tariffa='Tariffa '+str(user.tariffa), targhe=targhe)


@admin.route('/add_tariffa', methods=['POST'])
def add_tariffa():
    if request.method == 'POST':

        body = json.loads(request.data)

        tariffa = body["tariffa"]
        description = body["description"]

        # try to query last
        tar = Tariffa.query().order(-Tariffa.order).fetch()
        if len(tar) < 1:
            order = 1
        else:
            order = tar[0].order + 1

        # import tariffa
        tar = Tariffa()
        tar.tariffa = tariffa
        tar.order = order
        tar.description = description
        tar.put()
        flash("Tariffa aggiunta!")
        return redirect(url_for('auth.login'))


#---------- users -----------#


@admin.route('/del_user', methods=['GET'])
def del_user():
    if request.method == 'GET':
        user = request.args.get('user').split("_")
        name = user[0]
        surname = user[1]
        msg_del = DA.delete_user(name, surname)
        flash(msg_del)
        return redirect(url_for('auth.login'))
