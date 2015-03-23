from flask_script import Manager
from source.common.models import Base,engine
from source.api.api_server import app as rest_app
from source.website.web_server import app as web_app
from werkzeug.serving import run_simple

manager = Manager(rest_app)
@manager.command
def init_db():
    Base.metadata.create_all(bind=engine)

@manager.command
def run_api_server(is_public):
    is_public = 'True' == is_public
    if is_public:
        run_simple('0.0.0.0',4999, rest_app, use_debugger=True, use_reloader=True)
    else:
        run_simple('localhost',4999, rest_app, use_debugger=True, use_reloader=True)

@manager.command
def run_web_server(is_public):
    is_public = 'True' == is_public
    if is_public:
        run_simple('0.0.0.0',5000, web_app, use_debugger=True, use_reloader=True)
    else:
        run_simple('localhost',5000, web_app, use_debugger=True, use_reloader=True)


if __name__ == '__main__':
    manager.run()