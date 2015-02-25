from flask_script import Manager
from flask import Flask
from source.models import Base,engine
from source.server import app
manager = Manager(app)


@manager.command
def initdb(in_memory):
    Base.metadata.create_all(bind=engine)

@manager.command
def runserver():
    app.run(debug=True)

if __name__ == '__main__':
    manager.run()