import subprocess

from anyaudio import logger
from . import Scheduler


class YoutubeDLUpgrader(Scheduler):

    def __init__(self, name='<Youtube-dl upgrade', period=86400):
        Scheduler.__init__(self, name, period)

    def run(self):
        command = 'pip install --upgrade youtube-dl'
        logger.info('{0} Running : {1}'.format(self.name, command))
        subprocess.call(command, shell=True)
