import threading, time, queue, socket
from core.utils.utils import *

class pipe_queue():
    def __init__(self, name):
        self.queue = queue.Queue()
        self.name = name

    def queue_item(self, item):
        self.queue.put(item)
        # print(f" queue({self.name}): {item}")

    def dequeue_item(self):
        item = self.queue.get()
        # print(f" dequeue({self.name}): {item}")
        return item

    def queue_len(self):
        return self.queue.qsize()

class ThreadWrap(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.run_cond = True
        self.in_queue = pipe_queue("input")
        self.out_queue = pipe_queue("output")

    def is_blocking(self):
        return False

    def ask_to_stop(self):
        self.run_cond = False

    def stop(self):
        self.ask_to_stop()
        self.join()

class ConnectionThread(ThreadWrap):
    def __init__(self):
        ThreadWrap.__init__(self)

    def send(self, connection, in_queue):
        if in_queue.queue_len() == 0:
            return 0

        data = in_queue.dequeue_item()
        msg_bytes = obj2json2bytes(data)
        print(f"+++ {len(msg_bytes)}b")
        connection.sendall(msg_bytes)
        print(f"+++ wysłano")
        return 1

    def revice_data(self, connection):
        data = connection.recv(4)
        if not data:
            return None
        byte_size = int.from_bytes(data, byteorder="little")

        data = b''
        while len(data) < byte_size:
            packet = connection.recv(byte_size - len(data))
            if not packet:
                return None
            data += packet

        return data

    def recive(self, connection, out_queue):
        msg_bytes = self.revice_data(connection)
        print(f"+++ odebrano {len(msg_bytes)}b")
        new_data = bytes2json2obj(msg_bytes)
        if new_data is None:
            return -1000
        
        out_queue.queue_item(new_data)
        return 1

    def recive_nb(self, connection, out_queue):
        progres = 0
        connection.settimeout(0.1)
        try:
            progres = self.recive(connection, out_queue)
        except: 
            pass
        return progres

    def connection_loop(self, connection, conn_in_q, conn_out_q):
        while self.run_cond:
            # print("+++ connection loop")
            # print(f"{conn_in_q}")
            # print(f"{conn_out_q}")

            progress = 0
            progress += self.send(connection, conn_in_q)
            progress += self.recive_nb(connection, conn_out_q)
            if progress == 0:
                time.sleep(0.1)
            if progress < 0:
                break