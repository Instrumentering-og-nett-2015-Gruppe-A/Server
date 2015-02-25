import socket

from flask import Flask, Response
from flask_restful import Api
from source.api.resources import Mailboxes
from source.common.udp_brodcast import send as udp_broadcast


app = Flask(__name__)
api = Api(app)

api.add_resource(Mailboxes.Mailbox, '/api/mailbox', endpoint="list_mailbox")
api.add_resource(Mailboxes.Mailbox, '/api/mailbox/<int:mailbox_id>', endpoint="mailbox")

@app.route('/broadcast/')
def broadcast_server_address():
    address = socket.gethostbyname(socket.gethostname())
    print address
    udp_broadcast(address)
    return Response(status=200)
