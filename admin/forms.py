from wtforms import Form, StringField, validators, FloatField, PasswordField
from wtforms.widgets import TextArea

"""
Form dell'area amministrazione.
"""

class FormTariffa(Form):
    nome = StringField('nome', [validators.DataRequired()])
    descrizione = StringField('descrizione', [validators.DataRequired(), validators.NumberRange(min=0, max=3)], widget=TextArea())
    prezzo = FloatField('prezzo', [validators.DataRequired()])

class ModPw(Form):
    password = PasswordField('password', [validators.DataRequired(), validators.Length(min=5)])
    confirm_password = PasswordField('confirm_password', [validators.DataRequired(), validators.Length(min=5)])

class AddPlate(Form):
    targa = StringField('targa', [validators.DataRequired(), validators.Length(min=4, max=10)])


