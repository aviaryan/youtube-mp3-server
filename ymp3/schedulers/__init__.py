from threading import Thread
from time import sleep
from traceback import print_exc


class Scheduler():

    def __init__(self, name, period):
        self.name = name
        self.period = period

    def __str__(self):
        return self.name

    def start(self, wait=False):
        worker = Thread(target=self.run_repeater)
        worker.daemon = True
        worker.start()
        if wait:
            worker.join()
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
