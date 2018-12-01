from common.commons import get_username
from flask import *
from main.forms import AddPlate
from models.User_Model import User
from models.Tariffe_Model import Tariffa
from data_access import DataAccess as DA
from models.Booking_Model import Booking


main = Blueprint('main', __name__)

# Gestione utenti

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
            return redirect(url_for('main.parking', level='A'))
        elif command == "PAGA":
            return redirect(url_for('main.paga'))
        if command == "PROFILO":
            return redirect(url_for('main.profilo'))


# gestione profilo
@main.route('/profilo', methods=['GET','POST'])
def profilo():
    if request.method == 'GET':
        form = AddPlate(request.form)
        user = User().query(User.email == session['user']['email']).fetch(1)[0]

        tariffa = None
        descrizione = None
        prezzo = None
        tariffe = Tariffa.query().fetch()
        for i, tar in enumerate(tariffe):
            if (i + 1) == int(user.tariffa):
                tariffa = tar.tariffa
                descrizione = tar.description
                prezzo = tar.prezzo

        targhe = user.targa.split(",")
        return render_template('user/profilo.html', username=get_username(session), is_admin=session['user']['superuser'],
                               form=form, tariffa=tariffa, descr_tariffa=descrizione, prezzo_tariffa=prezzo,
                               targhe=targhe)

    elif request.method == 'POST':
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
            return render_template('user/profilo.html', username=get_username(session), is_admin=session['user']['superuser'],
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
            return render_template('user/profilo.html', username=get_username(session), is_admin=session['user']['superuser'],
                                   form=form, tariffa='Tariffa ' + str(user.tariffa), targhe=targhe)


@main.route('/contattaci', methods=['GET'])
def contattaci():
    return render_template('user/contattaci.html')


@main.route('/parking', methods=['GET', 'POST'])
def parking():
    if request.method == 'GET':
        piano = request.args.get('level')

        #TODO cercare parcheggi del piano considerato
        list = [(str(i), "btn btn-danger" if i == 777 else "btn btn-success" if i == 776 else "btn btn-warning") for i in range(1,41)]

        return render_template('user/prenota.html', level=piano, parking=list)
    elif request.method == 'POST':
        parking = request.form['parking']

        piano = parking[0]
        numero = parking[1:]

        #TODO cercare parcheggio e modificarne lo stato

        print '\n' + '\n' + parking
        return redirect(url_for('main.index'))


#TODO finire pagamento
@main.route('/paga', methods=['GET'])
def paga():
    if request.method == 'GET':
        uuid = session['user']['user_id']

        prenotazione = Booking.query(Booking.uuid == uuid).order(-Booking.start).fetch(1)

        if len(prenotazione) > 0 and prenotazione[0].stop is not None:
            return render_template('user/paga.html')
        else:
            return render_template('user/no_pagamenti.html', username=get_username(session))


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
    return render_template('user/profilo.html', username=get_username(session), is_admin=session['user']['superuser'],
                           form=form, tariffa='Tariffa ' + str(user.tariffa), targhe=targhe)





