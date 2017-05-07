import os
from functools import wraps
from subprocess import check_output
from anyaudio import LOCAL, logger
from flask import request, jsonify
from youtube_dl import YoutubeDL
from HTMLParser import HTMLParser
from database import log_api_call
from mutagen.mp4 import MP4, MP4Cover
from networking import open_page


FILENAME_EXCLUDE = '<>:"/\|?*;'
# semi-colon is terminator in header


def delete_file(path):
    """
    safely delete file. Needed in case of Asynchronous threads
    """
    try:
        os.remove(path)
    except Exception:
        pass


def get_ffmpeg_path():
    if os.environ.get('FFMPEG_PATH'):
        return os.environ.get('FFMPEG_PATH')
    elif not LOCAL:  # openshift
        return 'ffmpeg/ffmpeg'
    else:
        return 'ffmpeg'  # hoping that it is set in PATH


def get_video_info_ydl(vid_id):
    """
    Gets video info using YoutubeDL
    """
    ydl = YoutubeDL()
    try:
        info_dict = ydl.extract_info(vid_id, download=False)
        return info_dict
    except:
        return {}


def get_filename_from_title(title, ext='.mp3'):
    """
    Creates a filename from title
    """
    if not title:
        return 'music.mp3'
    title = HTMLParser().unescape(title)
    for _ in FILENAME_EXCLUDE:
        title = title.replace(_, ' ')  # provide readability with space
    return title[:40] + ext  # TODO - smart hunt


def html_unescape(text):
    """
    Remove &409D; type unicode symbols and convert them to real unicode
    """
    try:
        title = HTMLParser().unescape(text)
    except Exception:
        title = text
    return title


def record_request(func):
    """
    Wrapper to log a request
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        log_api_call(request)
        return func(*args, **kwargs)
    return wrapper


def add_cover(filename, video_id):
    raw_image = open_page('http://img.youtube.com/vi/%s/0.jpg' % video_id)

    audio = MP4(filename)
    cover = MP4Cover(raw_image)

    audio['covr'] = [cover]
    audio.save()


def get_download_link_youtube(vid_id, frmat):
    """
    gets the download link of a youtube video
    """
    command = 'youtube-dl https://www.youtube.com/watch?v=%s -f %s -g' % (vid_id, frmat)
    logger.info(command)
    retval = check_output(command.split())
    return retval.strip()


def make_error_response(msg, endpoint, code=500):
    """
    returns the error Response
    """
    return jsonify({
        'status': code,
        'requestLocation': endpoint,
        'developerMessage': msg,
        'userMessage': 'Some error occurred',
        'errorCode': '500-001'
    }), code
