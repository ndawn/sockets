import socket
import threading
from signal import pause

from config import BIND_ADDRESS
from config import WORKER_COUNT


def handle_connection(sock_: socket.socket):
    while True:
        client, address = sock_.accept()
        print(f'Accepted connection from {address}')
        while data := client.recv(4096):
            print(f'[{address}]: ', data.decode())
            client.send(data)
        print(f'Connection from {address} closed')


if __name__ == '__main__':
    sock = socket.socket(socket.AddressFamily.AF_INET, socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
    sock.bind(BIND_ADDRESS)
    sock.listen()
    print(f'Listening on port {BIND_ADDRESS.port}')

    stop = threading.Event()
    thread_pool = []
    for i in range(WORKER_COUNT):
        thread = threading.Thread(daemon=True, target=handle_connection, args=(sock,))
        thread_pool.append(thread)
        thread.start()

    try:
        pause()
    except (KeyboardInterrupt, SystemExit):
        print('Closing all connections')
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
