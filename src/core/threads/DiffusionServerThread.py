
import socket, time, select
from core.utils.utils_thread import ConnectionThread
from core.globals import get_server_port

class DiffusionServerThread(ConnectionThread):
    def __init__(self):
        ConnectionThread.__init__(self)
        self.worker = None
        self.host = 'localhost'
        self.port = get_server_port()

    def bind_worker(self, worker):
        self.worker = worker

    def config_host(self, host, port):
        self.host = host
        self.port = port

    def run(self):
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        server_address = (self.host, self.port)
        tcp_socket.bind(server_address)
        
        tcp_socket.listen(1)
        print(f"+++ Waiting for connection on port: {self.host}:{self.port}")
        while self.run_cond:
            time.sleep(0.1)
            readable, _w, _e = select.select([tcp_socket], [], [], 1)
            for s in readable:
                connection, client = s.accept()
                try:
                    print("+++ new client")
                    self.connection_loop(connection, self.worker.out_queue, self.worker.in_queue)
                finally:
                    connection.close()

        tcp_socket.close()