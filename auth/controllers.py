import hashlib
import uuid
import datetime
from common.commons import send_reset_pwd
from flask import *
from forms import UserLoginForm, UserRegistrationForm, PwdRecoveryForm
from models.User_Model import User
from models.Log_Model import Log
from models.Tariffe_Model import Tariffa
from data_access import DataAccess as DA
from models.Parking_Model import Parking
from random import randint

"""
Sezione Login.
"""

auth = Blueprint('auth', __name__)

###################
#    FUNCTIONS    #
###################

# controllo utente e caricamento dati in sezione
def login_user(form):
    try:
        user_data = User.query(User.email == form.email.data, User.password == hashlib.sha1(form.password.data).hexdigest()).fetch(1)
        if len(user_data) > 0:
            session['user'] = {
                "user_id": str(user_data[0].uuid),
                "nome": user_data[0].nome,
                "cognome": user_data[0].cognome,
                "email": user_data[0].email,
                "superuser": user_data[0].has_superuser,
                "active": user_data[0].is_valid,
                "authenticated": user_data[0].is_authenticated
            }
            return session['user']['authenticated']
        else:
            return False
    except:
        return False

# gestione Log accessi
def logging(user_id, type):
    log = Log()
    log.uuid = str(uuid.uuid4())
    log.user_id = str(user_id)
    log.timestamp = datetime.datetime.now()
    if type == "LOGIN":
        log.action = "LOGIN"
    else:
        log.action = "LOGOUT"
    log.put()

# inserimento utente nel database
def insert_user(form):
    try:
        check_user = User.query(User.email == form.email.data).fetch(1)
        if check_user > 0:
            u = User()
            u.uuid = str(uuid.uuid4())
            u.nome = form.nome.data
            u.cognome = form.cognome.data
            u.password = hashlib.sha1(form.password.data).hexdigest()
            u.email = form.email.data

            # insert tariffa
            tariffe = Tariffa.query(Tariffa.visibilita == True).order(Tariffa.order).fetch()
            for i, tar in enumerate(tariffe):
                if (i+1) == int(form.tariffa.data):
                    u.tariffa = tar.tariffa

            u.targa = form.targa.data
            u.put()
            return True

        return False
    except:
        return False



###################
#    ENDPOINTS    #
###################

# gestione sign in
@auth.route('/sign', methods=['GET', 'POST'])
def login():
    # chiamata post -> controllo credenziali
    if request.method == 'POST':
        form = UserLoginForm(request.form)
        if form.validate():
            user = login_user(form)
            if user:
                if session['user']['active']:
                    logging(session['user']['user_id'], 'LOGIN')
                    if session['user']['superuser'] == True:
                        return redirect(url_for('admin.index')) #amministratore

                    return redirect(url_for('main.index')) #utente comune
                else:
                    session.pop('user', None)
                    return render_template('login/not_allowed.html') #utente non valido
            else:
                flash('Invalid credentials!')
                return render_template('login/login.html', form=form) #credenziali errate

    # chiamata get -> controllo utente in sessione
    else:
        if 'user' in session:
            if session['user']['active']:
                if session['user']['authenticated'] == True and session['user']['superuser'] == False:
                    return redirect(url_for('main.index')) #utente comune
                elif session['user']['authenticated'] == True and session['user']['superuser'] == True:
                    return redirect(url_for('admin.index')) #amministratore
            else:
                return render_template('login/not_allowed.html') #utente non valido

        return render_template('login/login.html', form=UserLoginForm()) #pagina log in


# gestione registrazione
@auth.route('/register', methods=['GET', 'POST'])
def register():
    # caricamento dati provenienti dal form
    if request.method == 'POST':
        if request.form['password'] != request.form['confirm_password']:
            flash('Le password inserite sono diverse!')
            return redirect(url_for('auth.register'))
        form = UserRegistrationForm(request.form)

        # per il check del form devo guardare anche le tariffe
        tariffe = Tariffa.query(Tariffa.visibilita == True).order(Tariffa.order).fetch()
        my_choices = []
        for i, tar in enumerate(tariffe):
            my_choices.append((str(i + 1), tar.tariffa))
        form.tariffa.choices = my_choices

        # check form
        if form.validate():
            if insert_user(form):
                return render_template('login/not_allowed.html')
            else:
                flash('Registration error!')
                return redirect(url_for('auth.register'))

    # caricamento vista registrazione
    elif request.method == 'GET':
        form = UserRegistrationForm()

        # aggiunta tariffe possibili
        tariffe = Tariffa.query(Tariffa.visibilita == True).order(Tariffa.order).fetch()
        my_choices = []
        for i, tar in enumerate(tariffe):
            my_choices.append((str(i + 1), tar.tariffa))
        form.tariffa.choices = my_choices

        if len(tariffe) > 0:
            return render_template('login/registration.html', form=form, len=len(tariffe),
                                   nomi_tariffe=[tar.tariffa for tar in tariffe],
                                   prezzo_tariffe=[tar.prezzo for tar in tariffe],
                                   descr_tariffe=[tar.description for tar in tariffe])
        else:
            return render_template('login/registration.html', form=form, len=1,
                                   nomi_tariffe=["Non ci sono tariffe."],
                                   descr_tariffe=["Tutti gratis, paliazzu!!"])


# logout
@auth.route('/logout')
def logout():
    if 'user' in session:
        user = session['user']['user_id']
        session.pop('user', None) #svuoto sessione
        logging(user, 'LOGOUT')
        return redirect(url_for('auth.login'))
    else:
        return redirect(url_for('auth.login'))


# recupero password
@auth.route('/pwd_recovery', methods=['GET', 'POST'])
def pwd_recovery():
    if request.method == 'POST':
        form = PwdRecoveryForm(request.form)
        if form.validate():
            msg = send_reset_pwd(form)
            flash(msg)
            return redirect(url_for('auth.login'))
        else:
            flash('Impossibile completare la richiesta')
            return redirect(url_for('auth.pwd_recovery'))
    else:
        return render_template('login/pwd_recovery.html', form=PwdRecoveryForm())


##############################
#    ENDPOINTS PROVVISORI    #
##############################

# /auth/add_data -> aggiunge i dati provvisori
@auth.route('/add_data', methods=['GET'])
def add_data():
    if request.method == 'GET':
        #utente
        usr = User()
        usr.nome = "Luca"
        usr.cognome = "Puggioninu"
        usr.uuid = str(uuid.uuid4())
        usr.password = hashlib.sha1("ciaone").hexdigest()
        usr.email = "l.puggioninu@gmail.com"
        usr.targa = "GF6543"
        usr.tariffa = "Tariffa 1"
        usr.is_valid = True
        usr.put()

        #admin
        usr = User()
        usr.nome = "Claudio"
        usr.cognome = "Marche"
        usr.uuid = str(uuid.uuid4())
        usr.password = hashlib.sha1("ciaone").hexdigest()
        usr.email = "cla.mar92@gmail.com"
        usr.tariffa = "Tariffa 1"
        usr.targa = "GF6543"
        usr.is_valid = True
        usr.has_superuser = True
        usr.put()

        #tariffa
        tar = Tariffa()
        tar.tariffa = 'Tariffa 1'
        tar.description = "La piu' bella gazz"
        tar.prezzo = 5.00
        tar.order = 1
        tar.visibilita = True
        tar.put()

        tar = Tariffa()
        tar.tariffa = 'Tariffa 2'
        tar.description = "La meno bella gazz"
        tar.order = 2
        tar.prezzo = 5.00
        tar.visibilita = False
        tar.put()

        #parcheggi
        state = ['Libero', 'Prenotato', 'Occupato', 'Fuori Servizio']
        for piano in ['A', 'B', 'C', 'D']:
            for i in range(1, 41):
                parking = Parking()
                parking.piano = piano
                parking.number = i
                parking.stato = state[randint(0,3)]
                parking.put()
        flash("Dati Aggiunti")
        return redirect(url_for('auth.login'))

