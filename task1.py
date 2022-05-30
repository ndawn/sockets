import socket

from config import BIND_ADDRESS


if __name__ == '__main__':
    sock = socket.socket(socket.AddressFamily.AF_INET, socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
    sock.bind(BIND_ADDRESS)
    sock.listen()
    print(f'Listening on port {BIND_ADDRESS.port}')

    try:
        while True:
            client, address = sock.accept()
            print(f'Accepted connection from {address}')
            while data := client.recv(4096):
                print(data.decode())
                client.send(data)
            print('Connection closed')
    except KeyboardInterrupt:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
