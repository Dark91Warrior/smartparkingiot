from wtforms import Form, StringField, validators, SelectField, TextAreaField, PasswordField
from wtforms.widgets import TextArea

"""
Form gestione utente.
"""


class AddPlate(Form):
    targa = StringField('targa', [validators.DataRequired(), validators.Length(min=4, max=10)])

class Prenota(Form):
    targa = SelectField('targa')
    parcheggio = StringField('parcheggio')

class Violazione(Form):
    violazione = TextAreaField('violazione', [validators.DataRequired(), validators.Length(min=4, max=200)])

class ModPw(Form):
    password = PasswordField('password', [validators.DataRequired(), validators.Length(min=5)])
    confirm_password = PasswordField('confirm_password', [validators.DataRequired(), validators.Length(min=5)])

class ConttataciForm(Form):
    oggetto = StringField('oggetto', [validators.DataRequired()])
    descrizione = StringField('descrizione', [validators.DataRequired(), validators.NumberRange(min=0, max=3)], widget=TextArea())
