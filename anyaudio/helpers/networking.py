from data import user_agents

import requests

from random import choice, uniform
from time import sleep
from traceback import print_exc


def get_user_agent():
    return choice(user_agents)


def get_request_content(url, user_agent, allow_redirects, params):

    req = requests.get(
        url,
        headers={
            'User-Agent': user_agent
        },
        allow_redirects=allow_redirects,
        params=params
    )

    return req.content


def post_request_content(url, allow_redirects, data):

    req = requests.post(
        url,
        data=data,
        allow_redirects=allow_redirects,
    )

    return req.content


def open_page(url, user_agent=get_user_agent(), sleep_lower_limit=0, sleep_upper_limit=0,
              allow_redirects=True, type='GET', params=None, data=None):
    """
    Load a page and return its content
    """
    try:
        sleep(
            uniform(
                sleep_lower_limit,
                sleep_upper_limit
            )
        )

        if type == 'GET':
            if not params:
                params = {}
            ret = get_request_content(
                url,
                user_agent,
                allow_redirects,
                params
            )
        else:
            if not data:
                data = {}
            ret = post_request_content(
                url,
                allow_redirects,
                data
            )
        return ret
    except Exception:
        print_exc()
