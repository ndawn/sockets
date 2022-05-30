import random
import socket
import string

from config import BIND_ADDRESS


CLIENT_COUNT = 5


def main():
    sockets = []

    for i in range(CLIENT_COUNT):
        sock = socket.socket(family=socket.AddressFamily.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
        sock.connect(BIND_ADDRESS)
        sockets.append(sock)

    try:
        while True:
            for sock in sockets:
                sock.send(''.join(random.choices(string.ascii_lowercase, k=16)).encode())
    except KeyboardInterrupt:
        for sock in sockets:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()


if __name__ == '__main__':
    main()
