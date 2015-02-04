from flask import Flask
from udp_brodcast import send as udp_broadcast
import socket
app = Flask(__name__)

@app.route('/broadcast/')
def broadcast_server_address():
    address = socket.gethostbyname(socket.gethostname())
    print address
    udp_broadcast(address)
    return "hello"


if __name__ == '__main__':
    app.run()