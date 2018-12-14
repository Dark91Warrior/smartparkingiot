import hashlib
import random
import string
from models.User_Model import User

"""
Funzioni per l'accesso ai dati in database o sessione
"""

#############################
#       Get Functions       #
#############################


def get_users(is_valid=None):
    if is_valid == None:
        return User().query().fetch()
    else:
        return User().query(User.is_valid == is_valid).fetch()

def get_user(user_id):
    return User().query(User.uuid == user_id).fetch()

def get_user_from_mail(mail):
    return User().query(User.email == mail).fetch()


#############################
#     Update Functions      #
#############################

def reset_pwd(email):

    user = get_user_from_mail(email)
    old_pwd = user[0].password

    try:
        user = get_user_from_mail(email)
        old_pwd = user[0].password
        new_pwd = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

        user[0].password = hashlib.sha1(new_pwd).hexdigest()

        return (user[0], new_pwd, old_pwd)
    except:
        return (False)


def update_user(user_id, type, form=None):
    try:
        user_list = get_user(user_id)
        user = user_list[0]
        if type == 'ACTIVATE':
            user.is_valid = True
            user.put()
            return 'Utente attivato!'
        elif type == 'UPDATE_PROFILE':
            user.nome = form.nome.data
            user.cognome = form.cognome.data
            user.email = form.email.data
            user.put()
            return 'Informazioni aggiornate'
        elif type == 'UPDATE_PASSWORD':
            if form.password.data == form.confirm_password.data:
                if hashlib.sha1(form.password.data).hexdigest() != user.password:
                    user.password = hashlib.sha1(form.password.data).hexdigest()
                    user.put()
                    return 'Password aggiornata'
                else:
                    return 'Inserire una password diversa dalla precedente'
            else:
                return 'Le password inserite sono diverse'
    except:
        return 'Errore'


#############################
#     Delete Functions      #
#############################


def delete_user(name, surname):
    try:
        # ndb.delete_multi(Models.Categorie.query(Models.Categorie.categoriaID == id).fetch(keys_only=True).get())
        User().query(User.nome == name and User.cognome == surname).fetch(1)[0].key.delete()
        return 'Utente rimosso!'
    except:
        return "Errore nell'eliminazione dell'utente!"

def delete_user_from_uuid(uuid):
    try:
        # ndb.delete_multi(Models.Categorie.query(Models.Categorie.categoriaID == id).fetch(keys_only=True).get())
        User().query(User.uuid == uuid).fetch(1)[0].key.delete()
        return True
    except:
        return False

def auth_user(name, surname):
    try:
        # ndb.delete_multi(Models.Categorie.query(Models.Categorie.categoriaID == id).fetch(keys_only=True).get())
        usr = User().query(User.nome == name and User.cognome == surname).fetch(1)[0]
        usr.is_valid = True
        usr.put()
        return 'Utente abilitato!'
    except:
        return "Errore nell'abilitazione dell'utente!"

def admin_user(name, surname):
    try:
        # ndb.delete_multi(Models.Categorie.query(Models.Categorie.categoriaID == id).fetch(keys_only=True).get())
        usr = User().query(User.nome == name and User.cognome == surname).fetch(1)[0]
        usr.has_superuser = True
        usr.put()
        return 'Utente admin!'
    except:
        return "Errore nell'admin dell'utente!"

def change_targa(uuid, targa):
    try:
        # ndb.delete_multi(Models.Categorie.query(Models.Categorie.categoriaID == id).fetch(keys_only=True).get())
        usr = User().query(User.uuid == uuid).fetch(1)[0]
        usr.targa = targa
        usr.put()
        return True
    except:
        return False
