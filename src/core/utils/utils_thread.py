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