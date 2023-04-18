import threading, time, queue, select
from core.utils.utils import *
from core.utils.utils_logging import my_print

class pipe_queue():
    def __init__(self, name):
        self.queue = queue.Queue()
        self.name = name

    def queue_item(self, item):
        self.queue.put(item)

    def dequeue_item(self):
        item = self.queue.get()
        return item

    def queue_len(self):
        return self.queue.qsize()

class ThreadWrap(threading.Thread):
    def __init__(self, name="noneame"):
        threading.Thread.__init__(self)
        self.name = name
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



class ConnectionThreadBase(ThreadWrap):
    def __init__(self, name="noname"):
        ThreadWrap.__init__(self, name)
    
    def print(self, msg):
        msg_with_name = f"{self.name} {msg}"
        my_print(msg_with_name)

    def send(self, connection, obj_2_send):
        msg_bytes = obj2json2bytes(obj_2_send)
        connection.sendall(msg_bytes)
        # self.print(f"+++ wysłano {len(msg_bytes)}b")

    def revice_data(self, connection):
        data = connection.recv(4)
        if data is None:
            self.print("+++ recive None 1")
            return None
        byte_size = int.from_bytes(data, byteorder="little")

        data = b''
        while len(data) < byte_size:
            packet = connection.recv(byte_size - len(data))
            if packet is None:
                self.print("+++ recive None 2")
                return None
            data += packet

        return data

    def recive(self, connection):
        msg_bytes = self.revice_data(connection)
        # self.print(f"+++ odebrano {len(msg_bytes)}b")
        if msg_bytes is None:
            return None

        new_data = bytes2json2obj(msg_bytes)
        return new_data

    def recive_nb(self, connection):
        ready, _, _ = select.select([connection], [], [], 0)
        if ready:
            return self.recive(connection)

        return None

class ConnectionThread(ConnectionThreadBase):
    def __init__(self, name="noname"):
        ConnectionThreadBase.__init__(self, name)
        self.connect_ack = False
        self.disconnect_ack = False

    def progress_balance(self, progress):
        if progress == 0:
            time.sleep(0.1)

    def process_information(self, information_obj, out_pipe):
        is_disconnect = "disconnect" in information_obj    
        if is_disconnect and not self.disconnect_ack:
            self.print(f"+++ diconnect obj recived")
            self.disconnect_ack = True

        is_connect = "connect" in information_obj    
        if is_connect and not self.connect_ack:
            self.print(f"+++ connect obj recived")
            self.connect_ack = True

        operate_normal = not is_connect and not is_disconnect   
        if operate_normal:
            out_pipe.queue_item(information_obj)
            

    def send_simple_obj(self, connection, key):
        simple_obj = { key:1}
        try:
            self.send(connection, simple_obj)
            self.print(f"+++ {key} obj sended")
        except:
            self.print(f"!!! {key} obj send failed")


    def connection_loop(self, connection, conn_in_q, conn_out_q):
        
        self.connect_ack = False
        self.disconnect_ack = False
        self.send_simple_obj(connection, "connect")
        while self.run_cond and not self.disconnect_ack:
            
            progress = 0
            if conn_in_q.queue_len():
                obj_2_send = conn_in_q.dequeue_item()
                self.send(connection, obj_2_send)
                progress += 1
            
            recived_obj = self.recive_nb(connection)
            if recived_obj:
                self.process_information(recived_obj, conn_out_q)
                progress += 1

            self.progress_balance(progress)
        
        if self.connect_ack and not self.disconnect_ack:
            self.send_simple_obj(connection, "disconnect")
            self.disconnect_ack = True

