from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, BigInteger
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlite3 import dbapi2 as sqlite
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()
engine = create_engine('sqlite://', module=sqlite)
Session = sessionmaker(bind=engine)


class Mailbox(Base):
    __tablename__ = 'mailboxes'
    id = Column(Integer, primary_key=True)
    has_mail = Column(Boolean, default=False)
    is_closed = Column(Boolean, default=False)
    opens_in = Column(BigInteger, default= None)
    display_text = Column(String, default="")


class MailboxKey(Base):
    __tablename__ = 'mailboxkeys'
    rfid = Column(String, primary_key=True)
    mailbox_id = Column(Integer, ForeignKey('mailboxes.id'), primary_key=True, autoincrement=True)
    mailbox = relationship("Mailbox", backref=backref('keys'))

    def __unicode__(self):
        return self.rfid

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String)
    password_hash = Column(String )
    mailbox_id = Column(Integer, ForeignKey('mailboxes.id'), nullable=True)
    mailbox = relationship('Mailbox',backref=backref('user'), uselist=False)
    is_admin = Column(Boolean, default=False)
    needs_password_reset = Column(Boolean, default=False)
    needs_activation = Column(Boolean, default=True)

    def __init__(self, username, password):
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def change_password(self, new_password):
        self.password_hash = generate_password_hash(new_password)

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __str__(self):

