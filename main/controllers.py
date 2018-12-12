from common.commons import get_username
from flask import *
from main.forms import AddPlate, Prenota, Violazione, ModPw, ConttataciForm
from models.User_Model import User
from models.Tariffe_Model import Tariffa
from models.Parking_Model import Parking
from models.Historic_Model import Historic
from data_access import DataAccess as DA
from models.Booking_Model import Booking
from google.appengine.api import mail
from utils.utils import publishMQTT
from datetime import datetime
import hashlib


main = Blueprint('main', __name__)


# funzione invio email a amministratori
def send_email(object, text):
    administrators = User().query(User.has_superuser==True).fetch()

    if len(administrators) > 0:
        try:
            for admin in administrators:
                mail.send_mail(sender="cla.mar92@gmail.com",
                               to=admin.email,
                               subject=object,
                               body=text)
            return True
        except:
            return False
    else:
        return False

# Gestione utenti autenticati

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
        form = AddPlate()
        user = User().query(User.uuid == session['user']['user_id']).fetch(1)[0]

        try:
            tar = Tariffa.query(Tariffa.tariffa == user.tariffa).fetch(1)[0]
            tariffa = tar.tariffa
            descrizione = tar.description
            prezzo = tar.prezzo
        except:
            tariffa = None
            descrizione = None
            prezzo = None

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


# modifica password
@main.route('/password', methods=['GET','POST'])
def password():
    if request.method == 'GET':
        form = ModPw()
        return render_template('user/modifica_password.html', form=form, user=get_username(session))
    elif request.method == 'POST':
        try:
            pw = request.form['password']

            # modifica password nel database
            user = User.query(User.uuid == session['user']['user_id']).fetch(1)[0]
            user.password = hashlib.sha1(pw).hexdigest()
            user.put()

            # logout
            flash("Modifica password avvenuta correttamente.")
            return redirect(url_for('auth.logout'))
        except:
            flash("Erroe nella modifica. Riprova piu' tardi.")
            return redirect(url_for('main.index'))


@main.route('/contattaci', methods=['GET','POST'])
def contattaci():
    if request.method == 'GET':
        form = ConttataciForm()
        return render_template('user/contattaci.html', form=form)
    elif request.method == 'POST':
        oggetto = request.form['oggetto']
        descrizione = request.form['descrizione']

        descrizione = "L'utente " + get_username(session) + " (con id: " + session['user']['user_id'] + "), ha " \
                      "utilizzato la sezione CONTATTACI. Di seguito la descrizione:\n" + descrizione
        send_email(oggetto, descrizione)
        flash("Comunicazione inviata correttamente")
        return redirect(url_for('main.profilo'))



@main.route('/parking', methods=['GET', 'POST'])
def parking():
    if request.method == 'GET':
        piano = request.args.get('level')

        parks = Parking().query(Parking.piano == piano).fetch()

        try:
            list_for_view = [(str(park.number), "btn btn-danger" if park.stato == 'Occupato'
                                        else "btn btn-success" if park.stato == 'Libero'
                                        else "btn btn-warning" if park.stato == 'Prenotato'
                                        else "btn btn-dark" if park.stato == 'Fuori Servizio'
                                        else "btn btn-primary") for park in parks]
            return render_template('user/prenota.html', level=piano, parking=list_for_view)
        except:
            flash('Errore nel caricamento dei parcheggi')
            redirect(url_for('main.index'))

    elif request.method == 'POST':
        # gestione pagina relativa al singolo parcheggio
        parking = request.form['parking']

        piano = parking[0]
        numero = int(parking[1:])

        park = Parking().query(Parking.piano == piano, Parking.number == numero).fetch(1)

        # se esiste il parcheggio
        if len(park) > 0:
            stato = park[0].stato

            user = User().query(User.email == session['user']['email']).fetch(1)[0]

            # targhe
            form = Prenota()
            targhe = user.targa.split(',')
            my_choices = []
            for i, tar in enumerate(targhe):
                my_choices.append((str(i + 1), tar))
            form.targa.choices = my_choices

            return render_template('user/parking.html', parking=parking, stato=stato, form=form, livello=piano)

        else:
            flash("Errore caricamento parcheggio")
            return redirect(url_for('main.index'))


@main.route('/prenota', methods=['GET','POST'])
def prenota():
    if request.method == 'GET':
        # gestione violazione
        violazione = request.args.get('violazione')
        parcheggio = request.args.get('parcheggio')

        if violazione == "option1":
            text = "Parcheggio gia' occupato"
        elif violazione == "option2":
            text = "Il parcheggio non identifica la mia auto"

        if violazione == "option3":
            return redirect(url_for('main.violazione', parcheggio=parcheggio))
        else:
            object = "[VIOLAZIONE COMUNE]"
            text = "L'utente " + get_username(session) + ", nel parcheggio " + parcheggio + \
                   ", ha riscontrato una violazione del tipo: " + \
                   text + "." + "\nRispondi all'email: " + session['user']['email']

            if send_email(object, text):
                flash('Violazione segnalata correttamente')
            else:
                flash("Errore nella segnalazione. Ti preghiamo di riprovare piu' tardi")

            return redirect(url_for('main.index'))

    elif request.method == 'POST':

        # check if exist a booking
        uuid = session['user']['user_id']
        prenotazione = Booking.query(Booking.uuid == uuid).order(-Booking.start).fetch(1)
        if len(prenotazione) > 0:
            if prenotazione[0].start is None:
                return render_template('user/prenotazione_in_corso.html', username=get_username(session),
                                   parking=prenotazione[0].parking)
            else:
                return redirect(url_for('main.paga'))

        parking = request.form['parcheggio']
        piano = parking[0]
        numero = int(parking[1:])

        park = Parking().query(Parking.piano == piano, Parking.number == numero).fetch(1)

        # se esiste il parcheggio
        if len(park) > 0:
            park[0].stato = "Prenotato"
            park[0].put()

            idx_targa = int(request.form['targa'])
            user = User().query(User.email == session['user']['email']).fetch(1)[0]
            targhe = user.targa.split(',')
            targa = targhe[idx_targa - 1]

            # send signal to arduino (p = prenotazione)
            if not publishMQTT(parking, "p"):
                flash("Errore nella prenotazione. Riprova")
                return redirect(url_for('main.index'))

            # creo prenotazione
            book = Booking()
            book.uuid = session['user']['user_id']
            book.name = session['user']['nome']
            book.surname = session['user']['cognome']
            book.targa = targa
            book.parking = parking
            book.put()

            flash("Prenotazione effettuata correttamente")
            return redirect(url_for('main.index'))

        else:
            flash("Errore nella prenotazione. Riprova.")
            return redirect(url_for('main.index'))


@main.route('/violazione', methods=['GET','POST'])
def violazione():
    if request.method == 'GET':
        parcheggio = request.args.get('parcheggio')
        form = Violazione()
        return render_template('user/violazione.html', form=form, parcheggio=parcheggio)

    elif request.method == 'POST':
        parcheggio = request.form['parcheggio']
        violazione = request.form['violazione']

        #invia un email all'amministratore, con la descrizione della violazione
        object = "[VIOLAZIONE RARA]"
        text = "L'utente " + get_username(session) + ", nel parcheggio " + parcheggio + \
               ", ha riscontrato una violazione (definita dallo stesso utente) del tipo:\n" + \
               violazione + "\nRispondi all'email: " + session['user']['email']

        if send_email(object, text):
            flash('Violazione segnalata correttamente')
        else:
            flash("Errore nella segnalazione. Ti preghiamo di riprovare piu' tardi")

        return redirect(url_for('main.index'))


@main.route('/cancella_prenotazione', methods=['GET','POST'])
def cancella_prenotazione():
    uuid = session['user']['user_id']
    Booking.query(Booking.uuid == uuid).order(-Booking.start).fetch(1)[0].key.delete()
    flash("Prenotazione cancellata correttamente")
    return redirect(url_for('main.index'))


@main.route('/paga', methods=['GET', 'POST'])
def paga():
    if request.method == 'GET':
        uuid = session['user']['user_id']

        prenotazione = Booking.query(Booking.uuid == uuid).order(-Booking.start).fetch(1)

        if len(prenotazione) > 0:

            if prenotazione[0].start is None:
                return render_template('user/prenotazione_in_corso.html', username=get_username(session),
                                       parking=prenotazione[0].parking)
            else:
                data_inizio = prenotazione[0].start.date().strftime("%d-%m-%Y")
                ora_inizio = prenotazione[0].start.time().strftime("%H:%M:%S")

                fmt = '%Y-%m-%d %H:%M:%S'
                dat_now = datetime.now()
                datetime_str = dat_now.strftime(fmt)
                prenotazione[0].stop = datetime.strptime(datetime_str, fmt)

                data_fine = dat_now.strftime('%d-%m-%Y')
                ora_fine = dat_now.strftime('%H:%M:%S')

                usr = User().query(User.uuid == uuid).fetch(1)[0]
                tar = Tariffa().query(Tariffa.tariffa == usr.tariffa).fetch(1)[0]
                costo_tariffa = tar.prezzo

                costo = round((prenotazione[0].stop - prenotazione[0].start).total_seconds()/3600 * costo_tariffa, 2)

                prenotazione[0].costo = costo
                prenotazione[0].put()

                return render_template('user/paga.html', data_inizio=data_inizio,
                                       ora_inizio=ora_inizio, data_fine=data_fine, ora_fine=ora_fine, costo=costo)
        else:
            return render_template('user/no_pagamenti.html', username=get_username(session))

    if request.method == 'POST':
        uuid = session['user']['user_id']
        try:
            # cerca prenotazione
            book = Booking.query(Booking.uuid == uuid).order(-Booking.start).fetch(1)[0]

            # crea storico prenotazione
            hist = Historic()
            hist.uuid = uuid
            hist.name = book.name
            hist.surname = book.surname
            hist.targa = book.targa
            hist.start = book.start
            hist.stop = book.stop
            hist.parking = book.parking
            hist.costo = book.costo
            hist.put()

            # cancella prenotazione
            book.key.delete()

            flash('Pagamento effettuato correttamente')
        except:
            flash('Errore nel pagamento. Riprova')
        return redirect(url_for('main.index'))


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





