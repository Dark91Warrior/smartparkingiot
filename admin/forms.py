from wtforms import Form, StringField, validators, FloatField
from wtforms.widgets import TextArea

class FormTariffa(Form):
    nome = StringField('nome', [validators.DataRequired()])
    descrizione = StringField('descrizione', [validators.DataRequired(), validators.NumberRange(min=0, max=3)], widget=TextArea())
    prezzo = FloatField('prezzo', [validators.DataRequired()])
