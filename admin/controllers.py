from common.commons import get_username
from flask import *
from models.User_Model import User
from models.Tariffe_Model import Tariffa
from data_access import DataAccess as DA
from forms import FormTariffa
import time

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
        if command == "GESTISCI":
            return redirect(url_for('admin.gestisci'))
        elif command == "TARIFFE":
            return redirect(url_for('admin.tariffe'))
        if command == "PROFILO":
            return redirect(url_for('admin.profilo'))

@admin.route('/profilo', methods=['GET'])
def profilo():
    return 0

@admin.route('/gestisci', methods=['GET'])
def gestisci():
    return 0

@admin.route('/tariffe', methods=['GET'])
def tariffe():
    # form
    form = FormTariffa()

    tariffe = Tariffa.query().fetch()
    if len(tariffe) > 0:
        return render_template('admin/tariffe_admin.html', len=len(tariffe),
                               nomi_tariffe=[tar.tariffa for tar in tariffe],
                               descr_tariffe=[tar.description for tar in tariffe],
                               prezzo_tariffe=[tar.prezzo for tar in tariffe],
                               form=form,
                               empty=False)
    else:
        return render_template('admin/tariffe_admin.html', len=1,
                               nomi_tariffe=["Non ci sono tariffe."],
                               descr_tariffe=["Tutti gratis, paliazzu!!"],
                               form=form,
                               empty=True)


@admin.route('/add_tariffa', methods=['POST'])
def add_tariffa():
    if request.method == 'POST':

        tariffa = request.form['nome']
        description = request.form['descrizione']
        prezzo = float(request.form['prezzo'])

        # try to query last
        tariffe = Tariffa.query().order(-Tariffa.order).fetch()
        if len(tariffe) < 1:
            order = 1
        else:
            order = tariffe[0].order + 1

        # import tariffa
        new_tar = Tariffa()
        new_tar.tariffa = tariffa
        new_tar.order = order
        new_tar.description = description
        new_tar.prezzo = prezzo
        new_tar.put()

        time.sleep(1)

        return redirect(url_for('admin.tariffe'))



@admin.route('/del_tariffa', methods=['POST'])
def del_tariffa():
    if request.method == 'POST':

        tariffa = request.form['command']

        Tariffa.query(Tariffa.tariffa == tariffa).fetch(1)[0].key.delete()

        time.sleep(1)

        return redirect(url_for('admin.tariffe'))


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
