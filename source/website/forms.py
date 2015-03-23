from flask_wtf import Form, RecaptchaField
from sqlalchemy.sql.functions import current_user
from wtforms import  ValidationError, IntegerField
from wtforms.fields.core import StringField
from wtforms.fields.html5 import EmailField
from wtforms.fields.simple import PasswordField
from wtforms.validators import Length, Required, EqualTo, Email, InputRequired
from source.common.models import User, Session, Mailbox


class MailboxLCDTextForm(Form):
    first_line = StringField('First line', validators=[InputRequired(),Length(max=16)])
    second_line = StringField('Second line', validators=[InputRequired(),Length(max=16)])

class UserForm(Form):
    username = StringField('Username', validators=[Length(min=4), InputRequired()])
    email = EmailField('Email', validators=[InputRequired(), Email()])
    def validate_username(self, field):
        session = Session()
        if session.query(User).filter(User.username==field.data).count() > 0:
            raise ValidationError('Username must be unique')

class CreateAdministratorForm(UserForm):
    password = PasswordField('Password', validators=[InputRequired(),Length(min=8,message='Password must be at least 8 characters long.')])
    password_repeat =PasswordField('Repeat password', validators=[InputRequired(), EqualTo('password', message="Passwords must match")])

    def validate_username(self, field):
        session = Session()
        if session.query(User).filter(User.username==field.data).count() > 0:
            raise ValidationError('Username must be unique')

class AssignMailboxForm(Form):
    user = IntegerField('User', validators=[InputRequired()])
    mailbox = IntegerField('Mailbox', validators=[InputRequired()])

    def validate_user(self, field):
        session = Session()
        if session.query(User).filter(User.id==field.data).count() == 0:
            raise ValidationError('User id out of range.')

    def validate_user(self, field):
        session = Session()
        if session.query(Mailbox).filter(User.id==field.data).count() == 0:
            raise ValidationError('Mailbox id out of range.')

class AccountRecoveryForm(Form):

    email = EmailField('Email', validators=[InputRequired(), Email()])
    def validate_email(self, field):
        session = Session()
        if session.query(User).filter(User.email==field.data).count() ==0:
            raise ValidationError('Could not find an account with that email.')


class ChangePasswordForm(Form):
    def __init__(self, user, **kwargs):
        self.user = user
        super(ChangePasswordForm, self).__init__(**kwargs)
    old_password = PasswordField('Old password', validators=[InputRequired(),Length(min=4)])
    password = PasswordField('Password', validators=[InputRequired(),Length(min=8, message='Password must be at least 8 characters long.')])
    password_repeat =PasswordField('Repeat password', validators=[InputRequired(),EqualTo('password_repeat', message="Passwords must match") ])

    def validate_old_password(self, field):
        if not self.user.check_password(field.data):
            raise ValidationError("Old password invalid")

    def validate_password(self, field):
        if field.data == self.old_password.data:
            raise ValidationError("New password must be different from the old password.")


class SelectPasswordForm(Form):
    password = PasswordField('Password', validators=[InputRequired(),Length(min=8, message='Password must be at least 8 characters long.')])
    password_repeat =PasswordField('Repeat password', validators=[InputRequired(),EqualTo('password_repeat', message="Passwords must match") ])




class LoginForm(Form):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
