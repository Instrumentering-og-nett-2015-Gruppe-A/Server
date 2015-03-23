from flask import url_for
from itsdangerous import Signer, BadSignature
from pip._vendor import requests


def send_user_confirmation_mail(app, user):
    signer = Signer(app.config['SECRET_KEY'], salt='confirmation')
    confirmation_token = signer.sign(user.username)
    response = requests.post(
        app.config['MAIL_SERVER'],
        auth=("api", app.config['MAIL_API_KEY']),
        data={"from": "Smartbox %s" % app.config['MAIL_SENDER'],
              "to": "%s <%s>" %(user.username, user.email),
              "subject": "Confirm your account.",
              "html": "Hi %s \n <br>" % user.username+
                      "A user has been created for your mailbox.<br> "
                      "Please confirm your account.<br>"
                      "<a href='http://%s%s'>Confirm account</a>" % (app.config['SERVER_NAME'], url_for('confirm', confirmation_token=confirmation_token)) })
    return response.status_code == 200

def get_username_from_confirmation_token(app, confirmation_token):
    signer = Signer(app.config['SECRET_KEY'], salt='confirmation')
    try:
        username = signer.unsign(confirmation_token)
    except BadSignature:
        return None
    return username