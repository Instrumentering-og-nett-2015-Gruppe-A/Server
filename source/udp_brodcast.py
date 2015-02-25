import select, socket
import sys
import time

PORT = 53005

def listen():
    port = PORT
    bufferSize = 1024

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('<broadcast>', port))
    s.setblocking(0)

    while True:
        result = select.select([s],[],[])
        msg = result[0][0].recv(bufferSize)
        print(msg)

def send(message):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 0))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    data = message
    s.sendto(data, ('<broadcast>', PORT))
    time.sleep(2)

if __name__ == '__main__':
    if sys.argv[1] == 'listen':
        listen()
    elif sys.argv[1] == 'broadcast':
        send(sys.argv[2])
