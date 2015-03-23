from datetime import timedelta
from flask import url_for
from itsdangerous import Signer, BadSignature, TimestampSigner, SignatureExpired
from pip._vendor import requests


def send_user_confirmation_mail(app, user):
    signer = Signer(app.config['SECRET_KEY'], salt='confirmation')
    confirmation_token = signer.sign(user.username)
    response = send_mail(app, user, subject='Confirm your account.', html=
                      "Hi %s \n <br>" % user.username+
                      "A user has been created for your mailbox.<br> "
                      "Please confirm your account.<br>"
                      "<a href='http://%s%s'>Confirm account</a>" % (app.config['SERVER_NAME'], url_for('confirm', confirmation_token=confirmation_token)))


    return response.status_code == 200

def get_username_from_confirmation_token(app, confirmation_token):
    signer = Signer(app.config['SECRET_KEY'], salt='confirmation')
    try:
        username = signer.unsign(confirmation_token)
    except BadSignature:
        return None
    return username

def send_account_recovery_mail(app, user):
    signer = TimestampSigner(app.config['SECRET_KEY'], salt='recovery')
    recovery_token = signer.sign(user.username)
    recovery_url = 'http://%s%s' %(app.config['SERVER_NAME'], url_for('recover_account', recovery_token=recovery_token))
    response = send_mail(app, user, subject='Account recovery', html=
                         "Hi %s \n <br>" % user.username+
                         "Someone has requested to reset the password for your account.<br>"
                         "If you wish to reset your password click the following link: <br>"
                        "<a href='%s'>%s</a> <br>" % (recovery_url, recovery_url) +
                         "This link will expire in one hour.")
    return response.status_code == 200

def get_username_from_recovery_token(app, recovery_token):
    signer = TimestampSigner(app.config['SECRET_KEY'], salt='recovery')
    try:
        username = signer.unsign(recovery_token, max_age=timedelta(hours=1).seconds)

    except (BadSignature, SignatureExpired) as e:
        return None

    return username

def send_mail(app,to,subject, html):
    return requests.post(
        app.config['MAIL_SERVER'],
        auth=("api", app.config['MAIL_API_KEY']),
        data={"from": "Smartbox %s" % app.config['MAIL_SENDER'],
              "to": "%s <%s>" %(to.username, to.email),
              "subject": subject,
              "html": html})