from flask_script import Manager
from source.common.models import Base,engine
from source.api.api_server import app as rest_app
from source.website.web_server import app as web_app

manager = Manager(rest_app)
@manager.command
def init_db():
    Base.metadata.create_all(bind=engine)

@manager.command
def run_api_server(is_public):
    if is_public:
        rest_app.run(host='0.0.0.0', debug=True)
    else:
        rest_app.run(debug=True)

@manager.command
def run_web_server(is_public):
    if is_public:
        web_app.run(host='0.0.0.0', debug=True)
    else:
        web_app.run(debug=True)

if __name__ == '__main__':
    manager.run()