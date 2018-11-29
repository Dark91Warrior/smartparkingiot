from wtforms import Form, StringField, validators

class AddPlate(Form):
    targa = StringField('targa', [validators.DataRequired(), validators.Length(min=4, max=10)])
