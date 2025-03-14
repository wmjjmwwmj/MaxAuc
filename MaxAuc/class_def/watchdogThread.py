import threading
import time


class WatchdogThread(threading.Thread):
    def __init__(self,  interval=5):
        super().__init__()
        self.interval = interval
        self.update_options_benefits = False
        self.running = True

    def run(self):
        while self.running:
            # 每隔指定的时间间隔触发任务更新
            time.sleep(self.interval)
            self.update_options_benefits = true

    def stop(self):
        self.running = False
