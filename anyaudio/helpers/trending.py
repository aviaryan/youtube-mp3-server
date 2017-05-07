import re
from os import environ
from anyaudio import logger
from networking import open_page
from encryption import get_key, encode_data
from helpers import html_unescape


def get_trending_videos(html):
    """
    Get trending youtube videos from html
    """
    regex = '<tr.*?data-video-id="(.*?)".*?src="(.*?)".*?<a cl.*?>(.*?)</a>.*?by.*?>(.*?)</a>.*?<span .*?>(.*?)</'

    raw_results = re.findall(
        regex,
        html,
        re.DOTALL
    )[:int(environ.get('PLAYLIST_VIDEOS_LIMIT', 100))]

    vids = []
    for raw_result in raw_results:
        try:
            url = 'https://www.youtube.com/watch?v=' + raw_result[0]
            html = open_page(url)
            vids.append(
                {
                    'id': raw_result[0],
                    'thumb': 'http://img.youtube.com/vi/{0}/0.jpg'.format(raw_result[0]),
                    'title': html_unescape(raw_result[2].strip().decode('utf-8')),
                    'uploader': raw_result[3].decode('utf8'),
                    'length': raw_result[4],
                    'views': get_views(html),
                    'get_url': encode_data(
                        get_key(), id=raw_result[0],
                        title=raw_result[2].strip(), length=raw_result[4]
                    ),
                    'description': html_unescape(get_description(html))
                }
            )
        except Exception as e:
            logger.info(
                'Getting trending video failed. Message: %s, Video: %s' % (
                    str(e), raw_result[0]
                )
            )
    return vids


def get_views(html):
    return re.findall(
        '<div class="watch-view-count">(.*?) ',
        html
    )[0]


def get_description(html):
    desc =  re.findall(
        '<p id="eow-description".*?>(.*?)</p></div',
        html
    )

    if len(desc) > 0:
        return desc[0]
    return ''
