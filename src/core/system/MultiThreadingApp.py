
import time

class MultiThreadingApp():
    def __init__(self):
        self.exit = False

    def exit_fn(self):
        self.exit = True

    def thread_launch(self, thread_list):
        print("+++ starting threads...")
        for t in thread_list: 
            t.start()
        # blocking 
        # keyboard interupt (CTRL+C)
        if thread_list[-1].is_blocking() == False:
            try:
                while True and not self.exit:
                    time.sleep(0.1)
            except:
                print("+++ Keyboard interrupt")

        print("+++ stoping threads...")
        for t in thread_list:
            t.stop()