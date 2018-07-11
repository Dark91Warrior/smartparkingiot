from wtforms import Form, StringField, PasswordField, validators


class UserLoginForm(Form):
    email = StringField('email', [validators.DataRequired()])
    password = PasswordField('password', [validators.DataRequired()])


class UserRegistrationForm(Form):
    nome = StringField('nome', [validators.DataRequired(), validators.Length(min=2, max=50)])
    cognome = StringField('cognome', [validators.DataRequired(), validators.Length(min=2, max=25)])
    email = StringField('email', [validators.DataRequired()])
    password = PasswordField('password', [validators.DataRequired(), validators.Length(min=5)])
    confirm_password = PasswordField('confirm_password', [validators.DataRequired(), validators.Length(min=5)])


class UserInfoModify(Form):
    nome = StringField('nome', [validators.DataRequired(), validators.Length(min=2, max=50)])
    cognome = StringField('cognome', [validators.DataRequired(), validators.Length(min=2, max=25)])
    email = StringField('email', [validators.DataRequired()])


class UserPwdChange(Form):
    password = PasswordField('password', [validators.DataRequired(), validators.Length(min=5)])
    confirm_password = PasswordField('confirm_password', [validators.DataRequired(), validators.Length(min=5)])


class PwdRecoveryForm(Form):
    email = StringField('email', [validators.DataRequired()])