import logging
from flask import Flask
from os import environ


app = Flask(__name__)
app.config['DEBUG'] = True

DATABASE_PATH = 'SQLite.db'
LOCAL = True
if environ.get('OPENSHIFT_PYTHON_IP'):
    LOCAL = False

# Logger
logger = logging.getLogger('anyaudio-server')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    '%(relativeCreated)6d %(threadName)s %(message)s'
))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


import views
