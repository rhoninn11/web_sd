import time

T = "c_timing"

class EdgeStats():
    def __init__(self):
        self.frame_processed = 0
        self.frame_in_process = 0
        self.frame_time_history = []

    def scan_freame(self, frame):
        if T in frame:
            self._frame_processd(frame)

    def _remember(self, time_info):
        self.frame_time_history.append(time_info)
        
        if len(self.frame_time_history) > 10:
            self.frame_time_history.pop(0)

    def _gen_timming_info(self, frame):
        init_ts = frame["metadata"]["ts"]
        finish_ts = time.perf_counter()
        central_end_2_end_time = finish_ts - init_ts
        timming_text = f"+++ end 2 end processing time (central): {central_end_2_end_time:.3f}s"
        return timming_text

    def _frame_processd(self, frame):
        self.frame_processed += 1
        self.frame_in_process -= 1

        t_info = self._gen_timming_info(frame)
        self._remember(t_info)

    def frame_timeing_init(self, frame):
        self.frame_in_process += 1
        
        if "metadata" not in frame:
            frame["metadata"] = {}

        frame["metadata"]["ts"] = time.perf_counter()

    def get_frame_processed_num(self):
        return self.frame_processed

    def get_frame_in_process_num(self):
        return self.frame_in_process

    def get_avg_process_time(self):
        time_sum = 0
        sample_num = len(self.frame_time_history)
        for sample in self.frame_time_history:
            time_sum += sample
        
        return time_sum/sample_num