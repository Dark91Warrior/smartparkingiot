from wtforms import Form, StringField, PasswordField, validators, SelectField


class UserLoginForm(Form):
    email = StringField('email', [validators.DataRequired()])
    password = PasswordField('password', [validators.DataRequired()])


class UserRegistrationForm(Form):
    nome = StringField('nome', [validators.DataRequired(), validators.Length(min=2, max=50)])
    cognome = StringField('cognome', [validators.DataRequired(), validators.Length(min=2, max=25)])
    email = StringField('email', [validators.DataRequired()])
    password = PasswordField('password', [validators.DataRequired(), validators.Length(min=5)])
    confirm_password = PasswordField('confirm_password', [validators.DataRequired(), validators.Length(min=5)])
    my_choices = [('1', 'Tariffa 1'), ('2', 'Tariffa 2'), ('3', 'Tariffa 3')]
    tariffa = SelectField('tariffa', choices=my_choices)



class UserInfoModify(Form):
    nome = StringField('nome', [validators.DataRequired(), validators.Length(min=2, max=50)])
    cognome = StringField('cognome', [validators.DataRequired(), validators.Length(min=2, max=25)])
    email = StringField('email', [validators.DataRequired()])


class UserPwdChange(Form):
    password = PasswordField('password', [validators.DataRequired(), validators.Length(min=5)])
    confirm_password = PasswordField('confirm_password', [validators.DataRequired(), validators.Length(min=5)])


class PwdRecoveryForm(Form):
    email = StringField('email', [validators.DataRequired()])
