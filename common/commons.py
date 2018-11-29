import logging
from data_access.DataAccess import *
from flask import render_template, jsonify
from google.appengine.api import mail
import yaml

DEFAULT_SENDER = 'cla.mar92@gmail.com'

def get_username(session):
    return session['user']['nome'].capitalize() + ' ' + session['user']['cognome'].capitalize()


def send_reset_pwd(form):
    try:
        user_data = reset_pwd(form.email.data)

        if user_data[0]:
            data = {
                'email': str(yaml.load(user_data[0].email)),
                'name': str(yaml.load(user_data[0].nome)),
                'cognome': str(yaml.load(user_data[0].cognome)),
                'subject': 'Recupero Password',
                'message': str(user_data[1])
            }
            user_data[0].put()
        else:
            user_data[0].password = str(yaml.load(user_data[2]))
            user_data[0].put()
            return 'Errore nella gestione della richiesta!'

        # render response email
        renderedEmail = render_template('common/mail.html', data=data)

        # send mail
        logging.warning(mail.send_mail(
            sender="%s <%s>" % ('MCLab IMS', DEFAULT_SENDER),
            to="%s <%s>" % (data['name'], data['email']),
            subject="Recupero Password: %s" % (data['name']),
            body=data['message'],
            html=renderedEmail
        ))

    except Exception as e:
        # Oh no, something went wrong
        # return response object with error status code
        logging.warning(e)
        resp = jsonify({
            'status': 400,
            'error': str(e)
        })

        resp.status_code = 400
        msg = 'Errore, recupero non risucito!'
        return msg

    # return response object with good status code
    resp = jsonify({
        'status': 'Message sent'
    })
    resp.status_code = 200
    msg = 'Recupero riuscito, guarda la tua casella di posta!'
    return msg