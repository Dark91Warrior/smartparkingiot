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
import json

auth = Blueprint('auth', __name__)

###################
#    FUNCTIONS    #
###################


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
            u.tariffa = form.tariffa.data
            u.targa = form.targa.data
            u.put()
            return True

        return False
    except:
        return False



###################
#    ENDPOINTS    #
###################

@auth.route('/sign', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form = UserLoginForm(request.form)
        if form.validate():
            user = login_user(form)
            if user:
                if session['user']['active']:
                    logging(session['user']['user_id'], 'LOGIN')
                    if session['user']['superuser'] == True:
                        return redirect(url_for('admin.index'))

                    return redirect(url_for('main.index'))
                else:
                    session.pop('user', None)
                    return render_template('login/not_allowed.html')
            else:
                flash('Invalid credentials!')
                return render_template('login/login.html', form=form)
    else:
        if 'user' in session:
            if session['user']['active']:
                if session['user']['authenticated'] == True and session['user']['superuser'] == False:
                    return redirect(url_for('main.index'))
                elif session['user']['authenticated'] == True and session['user']['superuser'] == True:
                    return redirect(url_for('admin.index'))
            else:
                return render_template('login/not_allowed.html')

        return render_template('login/login.html', form=UserLoginForm())


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form['password'] != request.form['confirm_password']:
            flash('Le password inserite sono diverse!')
            return redirect(url_for('auth.register'))
        form = UserRegistrationForm(request.form)

        # per il check del form devo guardare anche le tariffe
        tariffe = Tariffa.query().fetch()
        my_choices = []
        for i, tar in enumerate(tariffe):
            my_choices.append((str(i + 1), tar.tariffa))
        form.tariffa.choices = my_choices

        if form.validate():
            if insert_user(form):
                flash('Registrazione eseguita!')
                return redirect(url_for('auth.login'))
            else:
                flash('Registration error!')
                return redirect(url_for('auth.register'))
    else:
        form = UserRegistrationForm()

        tariffe = Tariffa.query().order(Tariffa.order).fetch()
        my_choices = []
        for i, tar in enumerate(tariffe):
            my_choices.append((str(i + 1), tar.tariffa))

        form.tariffa.choices = my_choices

        tariffe = Tariffa.query().fetch()
        if len(tariffe) > 0:
            return render_template('login/registration.html', form=form, len=len(tariffe),
                                   nomi_tariffe=[tar.tariffa for tar in tariffe],
                                   prezzo_tariffe=[tar.prezzo for tar in tariffe],
                                   descr_tariffe=[tar.description for tar in tariffe])
        else:
            return render_template('login/registration.html', form=form, len=1,
                                   nomi_tariffe=["Non ci sono tariffe."],
                                   descr_tariffe=["Tutti gratis, paliazzu!!"])


@auth.route('/logout')
def logout():
    if 'user' in session:
        user = session['user']['user_id']
        session.pop('user', None)
        logging(user, 'LOGOUT')
        return redirect(url_for('auth.login'))
    else:
        return redirect(url_for('auth.login'))


@auth.route('/pwd_recovery', methods=['GET', 'POST'])
def pwd_recovery():
    if request.method == 'POST':
        form = PwdRecoveryForm(request.form)
        if form.validate():
            msg = send_reset_pwd(form)
            flash(msg)
            return redirect(url_for('auth.pwd_recovery'))
        else:
            flash('Impossibile completare la richiesta')
            return redirect(url_for('auth.pwd_recovery'))
    else:
        return render_template('login/pwd_recovery.html', form=PwdRecoveryForm())


##############################
#    ENDPOINTS PROVVISORI    #
##############################


@auth.route('/del_user', methods=['GET'])
def del_user():
    if request.method == 'GET':
        user = request.args.get('user').split("_")
        name = user[0]
        surname = user[1]
        msg_del = DA.delete_user(name, surname)
        flash(msg_del)
        return redirect(url_for('auth.login'))


@auth.route('/auth_user', methods=['GET'])
def auth_user():
    if request.method == 'GET':
        user = request.args.get('user').split("_")
        name = user[0]
        surname = user[1]
        msg_del = DA.auth_user(name, surname)
        flash(msg_del)
        return redirect(url_for('auth.login'))


@auth.route('/admin_user', methods=['GET'])
def admin_user():
    if request.method == 'GET':
        user = request.args.get('user').split("_")
        name = user[0]
        surname = user[1]
        msg_del = DA.admin_user(name, surname)
        flash(msg_del)
        return redirect(url_for('auth.login'))

@auth.route('/add_admin', methods=['GET'])
def add_admin():
    if request.method == 'GET':
        usr = User()
        usr.nome = "Claudio"
        usr.cognome = "Marche"
        usr.uuid = str(uuid.uuid4())
        usr.password = hashlib.sha1("ciaone").hexdigest()
        usr.email = "cla.mar92@gmail.com"
        usr.is_valid = True
        usr.has_superuser = True
        usr.put()
        flash("Aggiunto amministratore")
        return redirect(url_for('auth.login'))

@auth.route('/add_user', methods=['GET'])
def add_user():
    if request.method == 'GET':
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
        return redirect(url_for('auth.login'))
