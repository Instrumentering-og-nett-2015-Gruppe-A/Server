import socket

from flask import Flask, Response
from flask_restful import Api
from resources import Mailboxes
from udp_brodcast import send as udp_broadcast


app = Flask(__name__)
api = Api(app)

api.add_resource(Mailboxes.Mailbox, '/mailbox', endpoint="list_mailbox")
api.add_resource(Mailboxes.Mailbox, '/mailbox/<int:mailbox_id>', endpoint="mailbox")

@app.route('/broadcast/')
def broadcast_server_address():
    address = socket.gethostbyname(socket.gethostname())
    print address
    while(True)
        udp_broadcast(address)
    return Response(status=200)
