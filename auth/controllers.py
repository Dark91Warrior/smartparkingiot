import hashlib
import uuid
import datetime
from common.commons import send_reset_pwd
from flask import *
from forms import UserLoginForm, UserRegistrationForm, PwdRecoveryForm
from models.User_Model import User
from models.Log_Model import Log

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
                        return redirect(url_for('main.index'))

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
                    return redirect(url_for('main.index'))
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
        if form.validate():
            if insert_user(form):
                return redirect(url_for('auth.login'))
            else:
                flash('Registration error!')
                return redirect(url_for('auth.registration'))
    else:
        return render_template('login/registration.html', form=UserRegistrationForm())


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




@auth.route('/make_users')
def make_users():
    u = User()
    u.uuid = str(uuid.uuid4())
    u.nome = "Claudio"
    u.cognome = "Marche"
    u.password = hashlib.sha1("12345").hexdigest()
    u.email = "calamar@email.com"
    u.has_superuser = True
    u.is_valid = True
    u.put()
    u2 = User()
    u2.uuid = str(uuid.uuid4())
    u2.nome = "Raimondo"
    u2.cognome = "Cossu"
    u2.password = hashlib.sha1("54321").hexdigest()
    u2.email = "rai.cossu@gmail.com"
    u2.has_superuser = True
    u2.is_valid = True
    u2.put()
    u2 = User()
    u2.uuid = str(uuid.uuid4())
    u2.nome = "Marco"
    u2.cognome = "Uras"
    u2.password = hashlib.sha1("1234567890").hexdigest()
    u2.email = "marcou@email.com"
    u2.has_superuser = True
    u2.is_valid = True
    u2.put()
    return 'ok'

