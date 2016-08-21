from threading import Thread
from time import sleep
from traceback import print_exc


class Scheduler():

    def __init__(self, name, period):
        self.name = name
        self.period = period

    def __str__(self):
        return self.name

    def start(self, daemon_mode=True):
        worker = Thread(target=self.run_repeater)
        worker.daemon = daemon_mode
        worker.start()
        return worker

    def run_repeater(self):
        while True:
            try:
                self.run()
                sleep(self.period)
            except Exception:
                print_exc()

    def run(self):
        raise NotImplementedError()
