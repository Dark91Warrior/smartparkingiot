from common.commons import get_username
from flask import *
from main.forms import AddPlate
from models.User_Model import User
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

# gestione menu
@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('base.html', username=get_username(session), is_admin=session['user']['superuser'])
    elif request.method == 'POST':
        command = request.form['command']
        if command == "PARKING":
            return render_template('parking.html', username=get_username(session), is_admin=session['user']['superuser'])
        elif command == "PAGA":
            return render_template('paga.html', username=get_username(session), is_admin=session['user']['superuser'])
        if command == "PROFILO":
            form = AddPlate(request.form)
            user = User().query(User.email == session['user']['email']).fetch(1)[0]
            targhe = user.targa.split(",")
            return render_template('profilo.html', username=get_username(session), is_admin=session['user']['superuser'], form=form, tariffa='Tariffa '+str(user.tariffa), targhe=targhe)


# gestione profilo
@main.route('/profilo', methods=['POST'])
def profilo():
    command = request.form['command'].split('_')
    if command[0] == "delete":
        targa = command[1]
        user = User().query(User.email == session['user']['email']).fetch(1)[0]
        targhe = user.targa.split(',')
        targhe.remove(targa)
        user.targa = ','.join(targhe)
        user.put()
        # form
        form = AddPlate(request.form)
        return render_template('profilo.html', username=get_username(session), is_admin=session['user']['superuser'],
                               form=form, tariffa='Tariffa ' + str(user.tariffa), targhe=targhe)
    elif command[0] == "add":
        targa = request.form['targa']
        user = User().query(User.email == session['user']['email']).fetch(1)[0]

        # check if exist
        targhe = user.targa.split(",")
        if targa == "":
            flash("Targa non valida!")
        else:
            if targa not in targhe:
                user.targa = user.targa + ',' + targa
                targhe = user.targa.split(",")
                user.put()
            else:
                flash("Targa precedentemente inserita!")

        # form
        form = AddPlate(request.form)
        return render_template('profilo.html', username=get_username(session), is_admin=session['user']['superuser'],
                               form=form, tariffa='Tariffa ' + str(user.tariffa), targhe=targhe)

# cancellazione utente
@main.route('/del_user', methods=['GET'])
def del_user():
    if request.method == 'GET':
        uuid = session['user']['user_id']
        if DA.delete_user_from_uuid(uuid):
            user = session['user']['user_id']
            session.pop('user', None)
            return redirect(url_for('auth.login'))
        else:
            flash("Errore nella cancellazione del profilo!")

# modifica targa
@main.route('/mod_targa', methods=['POST'])
def mod_targa():
    targa = request.form['targa']
    uuid = session['user']['user_id']
    if not DA.change_targa(uuid, targa):
        flash("Errore in modifica targa!")
    form = AddPlate(request.form)
    user = User().query(User.email == session['user']['email']).fetch(1)[0]
    targhe = user.targa.split(",")
    return render_template('profilo.html', username=get_username(session), is_admin=session['user']['superuser'],
                           form=form, tariffa='Tariffa ' + str(user.tariffa), targhe=targhe)





