from flask import Flask, render_template, request, url_for, flash, Response
from flask_login import login_required, LoginManager, login_user, current_user, logout_user
from flask import abort
from flask_bower import Bower
from source.common.udp_brodcast import send as broadcast
import socket
from flask_wtf import CsrfProtect
from itsdangerous import Signer
from pip._vendor import requests
from source.common.models import Session, Mailbox
from source.common.utils import get_or_404
from forms import MailboxLCDTextForm, LoginForm, UserForm, ChangePasswordForm, CreateAdministratorForm, \
    SelectPasswordForm, AssignMailboxForm
from source.common.models import User, Session
from source.website.decorators import admin_required
from source.website.util import send_user_confirmation_mail, get_username_from_confirmation_token
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import object_session, eagerload, joinedload
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.utils import redirect

app = Flask(__name__)
login_manager = LoginManager()
csrf = CsrfProtect()
Bower(app)
login_manager.init_app(app)
csrf.init_app(app)
app.config.from_object('source.config.Configuration')
app.login_manager.login_view = 'login'
app.login_manager.session_protection = 'strong'


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if current_user.needs_password_reset:
        flash('Please change your password.', 'info')
        return redirect(url_for('change_password'))
    if current_user.is_admin:
        return administrate()
    else:
        return view_mailbox()


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        form = ChangePasswordForm(user=current_user, obj=request.form)
    else:
        form = ChangePasswordForm(user=current_user)

    if form.validate_on_submit():
        session = object_session(current_user)
        current_user.change_password(form.password.data)
        current_user.needs_password_reset = False
        session.add(current_user)
        session.commit()
        flash('Password changed.', 'success')
        return redirect(url_for('index'))

    return render_template('user/change_password.html', form=form)


@app.route('/administrate/users', methods=['GET', 'POST'])
@admin_required
def administrate_users():


    session = Session()
    users = session.query(User).filter(User.is_admin==False)
    return render_template('admin/users.html',  users=users)

@app.route('/administrate/users/delete/<int:id>')
@admin_required
def delete_user(id):
    session = Session()
    user = get_or_404(session.query(User), id)
    session.delete(user)
    session.commit()
    flash("User deleted", 'info')
    return redirect(url_for('administrate_users'))

@app.route('/administrate/users/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    if request.method == 'POST':
        form = UserForm(request.form)
    else:
        form = UserForm()

    if form.validate_on_submit():
        session = Session()
        user = User(username=form.username.data, password="")
        user.email = form.email.data
        user.needs_activation = True
        session.add(user)

        if send_user_confirmation_mail(app, user):
            flash('User created. Activation instructions has been sent to %s' % user.email, 'success')
            session.commit()
        else:
            flash('Unable to send confirmation to %s' % user.email, 'danger')

        return redirect(url_for('administrate_users'))
    return render_template('admin/create_user.html', form=form)

@app.route('/administrate/mailboxes', methods=['GET', 'POST'])
@admin_required
def administrate_mailboxes():
    session= Session()
    if request.method == 'POST':
        form = AssignMailboxForm(request.form)
        if form.validate_on_submit():
            user = session.query(User).get(form.user.data)
            mailbox = session.query(Mailbox).get(form.mailbox.data)
            user.mailbox = mailbox
            session.commit()
            flash('Mailbox %d assigned to %s' % (mailbox.id, user.username), 'success')

    mailboxes = session.query(Mailbox).options(joinedload('user')).all()

    users = session.query(User).filter(User.is_admin==False).filter(User.mailbox == None).all()
    return render_template('admin/mailboxes.html', mailboxes=mailboxes, users=users, form=AssignMailboxForm())

@app.route('/administrate/mailboxes/<int:mailbox_id>/free')
@admin_required
def free_mailbox(mailbox_id):
    session = Session()
    mailbox = session.query(Mailbox).options(joinedload('user')).filter(Mailbox.id==mailbox_id).first()
    username = mailbox.user.username
    mailbox.user = None
    session.commit()
    flash('%s removed from mailbox %d' % (username, mailbox.id), 'success')
    return redirect(url_for('administrate_mailboxes'))

@app.route('/administrate', methods=['GET', 'POST'])
@admin_required
def administrate():

    return render_template('admin/overview.html')

@app.route('/view_mailbox', methods=['GET', 'POST'])
@login_required
def view_mailbox():
    if current_user.is_admin:
        abort(401)

    if current_user.mailbox == None:
        return render_template('view_mailbox.html')

    session = Session()
    mailbox = current_user.mailbox
    form = MailboxLCDTextForm(obj=mailbox)
    if form.validate_on_submit():
        mailbox.display_text = '%s\n%s' % (form.first_line, form.second_line)
        session.commit()

    return render_template('view_mailbox.html', mailbox=mailbox, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if not current_user.is_anonymous():
        return redirect(url_for('index'))

    session = Session()
    if session.query(User).filter(User.is_admin).count() == 0:
        return redirect(url_for('setup'))

    if request.method == 'GET':
        return render_template('login.html', form=LoginForm())

    form = LoginForm(request.form)
    if form.validate_on_submit():

        session = Session()
        user = session.query(User).filter(User.needs_activation==False).filter(User.username==form.username.data).first()
        if user and  user.check_password(form.password.data):
            if login_user(user, remember=True):
                return redirect(request.args.get("next") or url_for("index"))
            else:
                flash('Unknown error', 'danger')
        else:
            flash('Invalid username/password.', 'danger')

    else:
        flash('The form contains one or more errors', 'danger')

    return render_template('login.html', form=form)


@app.route('/setup', methods=['GET', 'POST'])
def setup():
    session = Session()
    if session.query(User).filter(User.is_admin).count() > 0:
        return redirect(url_for('index'))
    if request.method == 'POST':
        form = CreateAdministratorForm(request.form)
    else:
        form = CreateAdministratorForm()

    if form.validate_on_submit():
        session = Session()
        user = User(username=form.username.data, password=form.password.data)
        user.email = form.email.data
        user.is_admin = True
        user.needs_password_reset = False
        user.needs_activation = False
        session.add(user)
        session.commit()
        flash('Administrator user created. You may now log in.', 'success')
        return redirect(url_for('login'))
    else:
        flash('Please create an administrator user to get started.', 'info')
    return render_template('admin/setup.html', form=form)

@app.route('/confirm/<confirmation_token>', methods=['GET', 'POST'])
def confirm(confirmation_token):
    username = get_username_from_confirmation_token(app, confirmation_token)
    if not username:
        flash('Invalid confirmation link', 'danger')
        return redirect(url_for('login'))
    session = Session()
    user = session.query(User).filter(User.username == username).first()

    if not user.needs_activation:
        flash('Account already confirmed', 'warning')
        return redirect(url_for('login'))
    if request.method == 'POST':
        form = SelectPasswordForm(request.form)
    else:
        flash("Please create a password to confirm your account.", 'info')
        form = SelectPasswordForm()

    if form.validate_on_submit():
        user.change_password(form.password.data)
        user.needs_activation = False
        session.commit()
        flash("Account confirmed. You may now login.", 'success')
        return redirect(url_for('login'))

    return render_template('user/select_password.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def load_user(user_id):
    session = Session()
    return session.query(User).get(user_id)

app.login_manager.user_loader(load_user)

@app.route('/broadcast')
@admin_required
def broadcast_server_address():
    address = socket.gethostbyname(socket.gethostname())
    broadcast(address)
    return Response(status=200)
