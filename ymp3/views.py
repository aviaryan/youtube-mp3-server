import traceback
from ymp3 import logger
from flask import jsonify, request, render_template, url_for, make_response
from subprocess import check_output, call
from ymp3 import app, LOCAL

from helpers.search import get_videos, get_video_attrs
from helpers.helpers import delete_file, get_ffmpeg_path, get_filename_from_title
from helpers.encryption import get_key, encode_data, decode_data
from helpers.data import trending_playlist
from helpers.database import get_trending, log_api_call
from helpers.networking import open_page


@app.route('/')
def home():
    log_api_call(request)
    return render_template('/home.html')


@app.route('/api/v1/d/<path:url>')
def download_file(url):
    """
    Download the file from the server.
    First downloads the file on the server using wget and then converts it using ffmpeg
    """
    log_api_call(request)
    try:
        # decode info from url
        try:
            abr = int(request.args.get('bitrate', '128'))
            abr = abr if abr >= 64 else 128  # Minimum bitrate is 128
        except ValueError:
            abr = 128
        data = decode_data(get_key(), url)
        vid_id = data['id']
        url = data['url']
        filename = get_filename_from_title(data['title'])
        m4a_path = 'static/%s.m4a' % vid_id
        mp3_path = 'static/%s.mp3' % vid_id
        # ^^ vid_id regex is filename friendly [a-zA-Z0-9_-]{11}
        # download and convert
        command = 'wget -O %s %s' % (m4a_path, url)
        check_output(command.split())
        command = get_ffmpeg_path()
        command += ' -i %s -acodec libmp3lame -ab %sk %s -y' % (m4a_path, abr, mp3_path)
        call(command, shell=True)  # shell=True only works, return ret_code
        data = open(mp3_path, 'r').read()
        response = make_response(data)
        # set headers
        response.headers['Content-Disposition'] = 'attachment; filename=%s' % filename
        response.headers['Content-Type'] = 'audio/mpeg'  # or audio/mpeg3
        response.headers['Content-Length'] = str(len(data))
        # remove files
        delete_file(m4a_path)
        delete_file(mp3_path)
        # stream
        return response
    except Exception:
        logger.info(traceback.format_exc())
        return 'Bad things have happened', 500


@app.route('/api/v1/g')
def get_link():
    """
    Uses youtube-dl to fetch the direct link
    """
    log_api_call(request)
    try:
        url = request.args.get('url')

        data = decode_data(get_key(), url)
        vid_id = data['id']
        title = data['title']
        command = 'youtube-dl https://www.youtube.com/watch?v=%s -f m4a/bestaudio' % vid_id
        command += ' -g'
        logger.info(command)
        retval = check_output(command.split())
        retval = retval.strip()
        if not LOCAL:
            retval = encode_data(get_key(), id=vid_id, title=title, url=retval)
            retval = url_for('download_file', url=retval)

        ret_dict = {
            'status': 200,
            'requestLocation': '/api/v1/g',
            'url': retval
        }
        return jsonify(ret_dict)
    except Exception as e:
        logger.info(traceback.format_exc())
        return jsonify(
            {
                'status': 500,
                'requestLocation': '/api/v1/g',
                'developerMessage': str(e),
                'userMessage': 'Some error occurred',
                'errorCode': '500-001'
            }
        ), 500


@app.route('/api/v1/search')
def search():
    """
    Search youtube and return results
    """
    log_api_call(request)
    try:
        search_term = request.args.get('q')
        link = 'https://www.youtube.com/results?search_query=%s' % search_term
        link += '&sp=EgIQAQ%253D%253D'  # for only video
        raw_html = open_page(link)
        vids = get_videos(raw_html)
        ret_vids = []
        for _ in vids:
            temp = get_video_attrs(_)
            if temp:
                temp['get_url'] = '/api/v1' + temp['get_url']
                ret_vids.append(temp)

        ret_dict = {
            'metadata': {
                'q': search_term,
                'count': len(ret_vids)
            },
            'results': ret_vids,
            'status': 200,
            'requestLocation': '/api/v1/search'
        }
    except Exception as e:
        ret_dict = {
            'status': 500,
            'requestLocation': '/api/v1/search',
            'developerMessage': str(e),
            'userMessage': 'Some error occurred',
            'errorCode': '500-001'
        }

    return jsonify(ret_dict)


@app.route('/api/v1/trending')
def get_latest():
    """
    Get trending songs
    """
    log_api_call(request)
    try:
        max_count = int(request.args.get('number', '25'))
        if max_count <= 0:
            max_count = 1
        if max_count > 100:
            max_count = 100
    except ValueError:
        max_count = 25

    type = request.args.get('type', 'popular')
    if type not in [_[0] for _ in trending_playlist]:
        type = 'popular'

    ret_vids = get_trending(type, max_count, get_url_prefix='/api/v1/g?url=')

    ret_dict = {
        'metadata': {
            'count': len(ret_vids),
            'type': type
        },
        'results': ret_vids
    }

    return jsonify(ret_dict)


# @app.route('/v/<string:vid_id>')
# def get_video(vid_id):
#     """
#     Gets video info ..
#     """
#     data = get_video_info_ydl(vid_id)
#     if len(data) > 0:
#         return jsonify(data)
#     else:
#         return 'There was a problem', 400
