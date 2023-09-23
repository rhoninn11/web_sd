import time

from core.ScriptIndex import ScriptIndex
SI = ScriptIndex()

class EdgeStats():
    def __init__(self):
        self.req_count = 0
        self.req_in_process = 0
        self.req_time_history = []

    def __str__(self):
        return f"EdgeStats: req_count: {self.req_count} req_in_process: {self.req_in_process}"

    def _get_request_processed_num(self):
        return self.req_count

    def get_request_in_process_num(self):
        return self.req_in_process

    def _get_avg_process_time(self):
        time_sum = 0
        sample_num = len(self.req_time_history)
        for sample in self.req_time_history:
            time_sum += sample
        
        return time_sum/sample_num

    def request_metadata(self, request):
        fn_name = SI.detect_script_name(request)
        print(f"+++ request_metadata: {fn_name}")
        metadata = {}
        if fn_name:
            if "metadata" not in request[fn_name]:
                request[fn_name]["metadata"] = metadata
            else:
                metadata = request[fn_name]["metadata"]

        return metadata

    def _remember(self, time_info):
        self.req_time_history.append(time_info)
        
        if len(self.req_time_history) > 10:
            self.req_time_history.pop(0)

    def _timming_summary(self, result):
        metadata = self.request_metadata(result)

        init_ts = metadata["ts"]
        finish_ts = time.perf_counter()
        metadata["ts_f"] = finish_ts

        central_end_2_end_time = finish_ts - init_ts
        timming_summary = f"+++ end_to_end processing time (central): {central_end_2_end_time:.3f}s"
        
        return timming_summary

    def _request_processed(self, result):
        self.req_count += 1
        self.req_in_process -= 1
        timeing_summary = self._timming_summary(result)
        self._remember(timeing_summary)

    def track_request(self, request):
        self.req_in_process += 1
        metadata = self.request_metadata(request)
        metadata["ts"] = time.perf_counter()

    def summarize_result(self, result):
        keys = result.keys()
        # print(f"+++ summarize_result: {keys}")
        if SI.stats_detect_script_name(result):
            metadata = self.request_metadata(result)
            if "ts" in metadata:
                self._request_processed(result)