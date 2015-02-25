from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlite3 import dbapi2 as sqlite


engine = create_engine('sqlite+pysqlite:///:database.db:', module=sqlite)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Mailbox(Base):
    __tablename__ = 'mailboxes'
    id = Column(Integer, primary_key=True)
    has_mail = Column(Boolean, default=False)


class MailboxKey(Base):
    __tablename__ = 'mailboxkeys'
    rfid = Column(String, primary_key=True)
    mailbox_id = Column(Integer, ForeignKey('mailboxes.id'))
    mailbox = relationship("Mailbox", backref=backref('keys'))