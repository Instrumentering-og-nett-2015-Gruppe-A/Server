from flask_script import Manager
from flask import Flask
from source.models import Base,engine
from source.server import app
manager = Manager(app)


@manager.command
def initdb():
    Base.metadata.create_all(bind=engine)

@manager.command
def runserver(is_public):
    if is_public:
        app.run(host='0.0.0.0', debug=True)
    else:
        app.run(debug=True)

if __name__ == '__main__':
    manager.run()