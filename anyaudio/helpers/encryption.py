import base64
import os
import json


def encode(key, clear):
    st = ''
    incr = get_key_hash(key)
    for _ in clear:
        st += unichr(incr + ord(_))
    return base64.urlsafe_b64encode(st.encode('utf-8'))


def decode(key, enc):
    st = ''
    enc = enc.replace('-', '+').replace('_', '/')
    enc = base64.b64decode(enc)  # dont know why urlsafe decode doesn't work
    incr = get_key_hash(key)
    for _ in enc:
        st += unichr(ord(_) - incr)
    return st


def get_key():
    return os.environ.get('SECRET_KEY', 'default key')


def get_key_hash(key):
    c = 0
    for _ in key:
        c += ord(_)
    return c % 20


def encode_data(key, **kwargs):
    data = json.dumps(kwargs, ensure_ascii=False, indent=None)
    return encode(key, data)


def decode_data(key, data):
    dec = decode(key, data)
    return json.loads(dec)
