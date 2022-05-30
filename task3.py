import errno
import socket
import threading
from dataclasses import dataclass
from signal import pause
from typing import Any
from typing import Callable
from typing import List
from typing import Tuple

from config import BIND_ADDRESS
from config import WORKER_COUNT


ClientTuple = Tuple[socket.socket, Tuple[str, int]]


@dataclass
class ClientSocket:
    socket: ClientTuple
    locked: bool = False


def handle_non_blocking_method(method: Callable, *args) -> Any:
    try:
        return method(*args)
    except IOError as exc:
        if exc.errno == errno.EWOULDBLOCK:
            return None
        raise


class WorkerThread(threading.Thread):
    def __init__(self, accepted_pool: List[ClientSocket], stop: threading.Event, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._accepted = accepted_pool
        self._stop_event = stop

    def run(self):
        while not self._stop_event.is_set():
            current_pool = self._accepted.copy()

            for client in current_pool:
                if client.locked:
                    continue

                client.locked = True
                sock, (host, port) = client.socket

                try:
                    data = sock.recv(4096)
                except IOError as exc:
                    if exc.errno == errno.EWOULDBLOCK:
                        client.locked = False
                        continue
                    raise

                if data:
                    print(f'[{host}:{port}]:', data.decode().rstrip('\n'))
                    try:
                        sock.send(data)
                    except IOError as exc:
                        if exc.errno == errno.EWOULDBLOCK:
                            pass
                        raise
                    client.locked = False
                else:
                    sock.shutdown(socket.SHUT_RDWR)
                    sock.close()
                    self._accepted.remove(client)
                    print(f'Connection with {host}:{port} closed')


class AcceptorThread(threading.Thread):
    def __init__(
        self,
        sock_: socket.socket,
        accepted_pool: List[ClientSocket],
        stop_: threading.Event,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._sock = sock_
        self._stop_event = stop_
        self._accepted = accepted_pool

    def run(self):
        while not self._stop_event.is_set():
            try:
                client_tuple = self._sock.accept()
            except IOError as exc:
                if exc.errno == errno.EWOULDBLOCK:
                    continue
                raise
            client, (host, port) = client_tuple
            client.setblocking(False)
            self._accepted.append(ClientSocket(client_tuple))
            print(f'Accepted connection from {host}:{port}')

    def stop(self):
        stop_sock = socket.socket(
            family=socket.AddressFamily.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
        stop_sock.connect(BIND_ADDRESS)
        stop_sock.close()


def main():
    sock = socket.socket(socket.AddressFamily.AF_INET, socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
    sock.bind(BIND_ADDRESS)
    sock.listen()
    print(f'Listening on port {BIND_ADDRESS.port}')

    stop = threading.Event()
    worker_pool = []
    accepted_pool = []

    acceptor = AcceptorThread(sock, accepted_pool, stop)
    acceptor.start()

    for i in range(WORKER_COUNT):
        worker = WorkerThread(accepted_pool, stop)
        worker_pool.append(worker)
        worker.start()

    try:
        pause()
    except (KeyboardInterrupt, SystemExit):
        print('Closing all connections')
        stop.set()

        acceptor.stop()

        for worker in worker_pool:
            worker.join()

        acceptor.join()
    finally:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()


if __name__ == '__main__':
    main()
