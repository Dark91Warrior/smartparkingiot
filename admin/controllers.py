from common.commons import get_username
from flask import *
from models.User_Model import User
from models.Tariffe_Model import Tariffa
from models.Parking_Model import Parking
from data_access import DataAccess as DA
from forms import FormTariffa, ModPw, AddPlate
import time
import hashlib

"""
Gestione amministrazione
"""

admin = Blueprint('admin', __name__)

# controllo se l'utente e' presente in se4ssione (per non fare il login).
# Prescinde l'utilizzo di cookies
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


# ---------- items -----------#

# gestione menu
@admin.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('base.html', username=get_username(session), is_admin=session['user']['superuser'])
    elif request.method == 'POST':
        command = request.form['command']
        if command == "PARKING":
            return redirect(url_for('admin.gestisci', level='A'))
        elif command == "TARIFFE":
            return redirect(url_for('admin.tariffe'))
        if command == "PROFILO":
            return redirect(url_for('admin.profilo'))


# area profilo
@admin.route('/profilo', methods=['GET', 'POST'])
def profilo():
    if request.method == 'GET':
        form = AddPlate()
        user = User().query(User.uuid == session['user']['user_id']).fetch(1)[0]
        targhe = user.targa.split(",")

        return render_template('admin/profilo.html', username=get_username(session), form=form, targhe=targhe)
    # gestione aggiungi o cancella targa
    elif request.method == 'POST':
        command = request.form['command'].split('_')
        if command[0] == "delete":
            targa = command[1]
            user = User().query(User.email == session['user']['email']).fetch(1)[0]
            targhe = user.targa.split(',')
            targhe.remove(targa)
            user.targa = ','.join(targhe)
            user.put()

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
        # attesa per salvataggio in database
        time.sleep(1)
        return redirect(url_for('admin.profilo'))


# sezione gestisci
@admin.route('/gestisci', methods=['GET', 'POST'])
def gestisci():
    if request.method == 'GET':
        piano = request.args.get('level')

        parks = Parking().query(Parking.piano == piano).fetch()

        # classi per i diversi bottoni
        try:
            list_for_view = [(str(park.number), "btn btn-danger" if park.stato == 'Occupato'
            else "btn btn-success" if park.stato == 'Libero'
            else "btn btn-warning" if park.stato == 'Prenotato'
            else "btn btn-dark" if park.stato == 'Fuori Servizio'
            else "btn btn-primary") for park in parks]
            return render_template('admin/gestisci.html', level=piano, parking=list_for_view)
        except:
            flash('Errore nel caricamento dei parcheggi')
            redirect(url_for('admin.index'))

    elif request.method == 'POST':
        # gestione pagina relativa al singolo parcheggio
        parking = request.form['parking']

        piano = parking[0]
        numero = int(parking[1:])

        park = Parking().query(Parking.piano == piano, Parking.number == numero).fetch(1)

        # se esiste il parcheggio
        if len(park) > 0:
            stato = park[0].stato

            return render_template('admin/parking.html', parking=parking, stato=stato, livello=piano)

        else:
            flash("Errore caricamento parcheggio")
            return redirect(url_for('admin.index'))


# gestione modifica stato parcheggio dall'area relativa al singolo parcheggio
@admin.route('/parking', methods=['POST'])
def parking():
    command = request.form['command']
    parking = request.form['parcheggio']

    piano = parking[0]
    numero = int(parking[1:])

    try:
        park = Parking().query(Parking.piano == piano, Parking.number == numero).fetch(1)

        if command == 'libera':
            park[0].stato = 'Libero'
        elif command == 'occupa':
            park[0].stato = 'Occupato'

        stato = park[0].stato
        park[0].put()

        return render_template('admin/parking.html', parking=parking, stato=stato, livello=piano)
    except:
        flash("Errore modifica parcheggio")
        return redirect(url_for('admin.index'))


# settaggio fuori servizio del singolo parcheggio
@admin.route('/fuori_servizio', methods=['POST'])
def fuori_servizio():
    parking = request.form['fuori_servzio']

    piano = parking[0]
    numero = int(parking[1:])
    stato = "Fuori Servizio"

    try:
        park = Parking().query(Parking.piano == piano, Parking.number == numero).fetch(1)
        park[0].stato = stato
        park[0].put()
        return render_template('admin/parking.html', parking=parking, stato=stato, livello=piano)
    except:
        flash("Errore modifica parcheggio")
        return redirect(url_for('admin.index'))


# sezione tariffe
@admin.route('/tariffe', methods=['GET'])
def tariffe():
    # form
    form = FormTariffa()

    tariffe = Tariffa.query().order(Tariffa.order).fetch()
    if len(tariffe) > 0:
        return render_template('admin/tariffe_admin.html', len=len(tariffe),
                               nomi_tariffe=[tar.tariffa for tar in tariffe],
                               descr_tariffe=[tar.description for tar in tariffe],
                               prezzo_tariffe=[tar.prezzo for tar in tariffe],
                               visibilita=[True if tar.visibilita is True else False for tar in tariffe],
                               form=form,
                               empty=False)
    else:
        return render_template('admin/tariffe_admin.html', len=1,
                               nomi_tariffe=["Non ci sono tariffe."],
                               descr_tariffe=["Tutti gratis, paliazzu!!"],
                               form=form,
                               empty=True)

# aggiungi una tariffa
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


# modifica stato tariffa (Visibile o Non Visibile)
@admin.route('/mod_tariffa', methods=['POST'])
def mod_tariffa():
    if request.method == 'POST':

        try:
            tariffa = request.form['command-add']
            comando = "aggiungi"
        except:
            pass

        try:
            tariffa = request.form['command-del']
            comando = "cancella"
        except:
            pass

        tar = Tariffa.query(Tariffa.tariffa == tariffa).fetch(1)[0]
        if comando == "aggiungi":
            tar.visibilita = True
        # la tariffa non viene cancellata
        # per non compromettere gli utenti che la utilizzano fin'ora
        elif comando == "cancella":
            tar.visibilita = False

        tar.put()
        time.sleep(1)
        return redirect(url_for('admin.tariffe'))


# cancellazione utente
@admin.route('/del_user', methods=['GET'])
def del_user():
    if request.method == 'GET':
        uuid = session['user']['user_id']
        if DA.delete_user_from_uuid(uuid):
            user = session['user']['user_id']
            session.pop('user', None)
            return redirect(url_for('auth.login'))
        else:
            flash("Errore nella cancellazione del profilo!")

# modifica password
@admin.route('/password', methods=['GET','POST'])
def password():
    if request.method == 'GET':
        form = ModPw()
        return render_template('admin/modifica_password.html', form=form, user=get_username(session))
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
            return redirect(url_for('admin.index'))

# modifica targa nella sezione profilo
@admin.route('/mod_targa', methods=['POST'])
def mod_targa():
    targa = request.form['targa']
    uuid = session['user']['user_id']
    if not DA.change_targa(uuid, targa):
        flash("Errore in modifica targa!")
    return redirect(url_for('admin.profilo'))