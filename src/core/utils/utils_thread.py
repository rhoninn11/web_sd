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
    
    def send(self, connection, obj_2_send):
        msg_bytes = obj2json2bytes(obj_2_send)
        print(f"+++ {len(msg_bytes)}b")
        connection.sendall(msg_bytes)
        print(f"+++ wysłano")

    def revice_data(self, connection):
        data = connection.recv(4)
        if data is None:
            return None
        byte_size = int.from_bytes(data, byteorder="little")

        data = b''
        while len(data) < byte_size:
            packet = connection.recv(byte_size - len(data))
            if packet is None:
                return None
            data += packet

        return data

    def recive(self, connection):
        msg_bytes = self.revice_data(connection)
        print(f"+++ odebrano {len(msg_bytes)}b")
        if msg_bytes is None:
            return None

        new_data = bytes2json2obj(msg_bytes)
        return new_data

    def recive_nb(self, connection):
        try:
            connection.settimeout(0.1)
            return self.recive(connection)
        except: 
            pass
        return None

    def progress_balance(self, progress):
        if progress == 0:
            time.sleep(0.1)


    def connection_loop(self, connection, conn_in_q, conn_out_q):
        
        conn_end = False
        while self.run_cond and not conn_end:
            
            progress = 0
            if conn_in_q.queue_len():
                obj_2_send = conn_in_q.dequeue_item()
                self.send(connection, obj_2_send)
                progress += 1
            
            rcv_obj = self.recive_nb(connection)
            if rcv_obj:
                conn_end = "disconnect" in rcv_obj    
                if not conn_end:
                    conn_out_q.queue_item(rcv_obj)
                progress += 1

            self.progress_balance(progress)
        
        if not conn_end:
            print(f"+++ disconnect inform other side")
            conn_end_obj = {"disconnect":1}
            self.send(connection, conn_end_obj)
