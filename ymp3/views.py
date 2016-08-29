import traceback

import requests
from flask import Response

from ymp3 import logger
from flask import jsonify, request, render_template, url_for, make_response, Markup
from subprocess import check_output, call
from ymp3 import app, LOCAL

from helpers.search import get_videos, get_video_attrs, extends_length
from helpers.helpers import delete_file, get_ffmpeg_path, get_filename_from_title, \
    record_request, add_cover
from helpers.encryption import get_key, encode_data, decode_data
from helpers.data import trending_playlist
from helpers.database import get_trending, get_api_log
from helpers.networking import open_page


@app.route('/')
@record_request
def home():
    return render_template('/home.html')


@app.route('/beta')
@record_request
def home_beta():
    return render_template('/index.html')


@app.route('/explore')
@record_request
def explore():
    search_query = request.args.get('q')
    if search_query:
        search_query = '"{0}"'.format(search_query.replace('\"', '\\\"').strip())
    else:
        search_query = '""'

    playlist = request.args.get('p')
    if playlist:
        playlist = '"{0}"'.format(playlist.replace('\"', '\\\"').strip())
    else:
        playlist = '""'
    return render_template('/explore.html', query=Markup(search_query), playlist=Markup(playlist))


@app.route('/api/v1/d')
@record_request
def download_file():
    """
    Download the file from the server.
    First downloads the file on the server using wget and then converts it using ffmpeg
    """
    try:
        url = request.args.get('url')
        download_format = request.args.get('format', 'm4a')
        try:
            abr = int(request.args.get('bitrate', '128'))
            abr = abr if abr >= 64 else 128  # Minimum bitrate is 128
        except ValueError:
            abr = 128
        download_album_art = request.args.get('cover', 'false').lower()
        # decode info from url
        data = decode_data(get_key(), url)
        vid_id = data['id']
        url = data['url']
        filename = get_filename_from_title(data['title'], ext='')
        m4a_path = 'static/%s.m4a' % vid_id
        mp3_path = 'static/%s.mp3' % vid_id
        # ^^ vid_id regex is filename friendly [a-zA-Z0-9_-]{11}
        # download and convert
        command = 'wget -O %s %s' % (m4a_path, url)
        check_output(command.split())
        if download_album_art == 'true':
            add_cover(m4a_path, vid_id)
        if download_format == 'mp3':
            if extends_length(data['length'], 20 * 60):  # sound more than 20 mins
                raise Exception()
            command = get_ffmpeg_path()
            command += ' -i %s -acodec libmp3lame -ab %sk %s -y' % (m4a_path, abr, mp3_path)
            call(command, shell=True)  # shell=True only works, return ret_code
            with open(mp3_path, 'r') as f:
                data = f.read()
            content_type = 'audio/mpeg'  # or audio/mpeg3'
            filename += '.mp3'
        else:
            with open(m4a_path, 'r') as f:
                data = f.read()
            content_type = 'audio/mp4'
            filename += '.m4a'
        response = make_response(data)
        # set headers
        # http://stackoverflow.com/questions/93551/how-to-encode-the-filename-
        response.headers['Content-Disposition'] = 'attachment; filename="%s"' % filename
        response.headers['Content-Type'] = content_type
        response.headers['Content-Length'] = str(len(data))
        # remove files
        delete_file(m4a_path)
        delete_file(mp3_path)
        # stream
        return response
    except Exception as e:
        logger.info('Error %s' % str(e))
        logger.info(traceback.format_exc())
        return 'Bad things have happened', 500


@app.route('/api/v1/g')
@record_request
def get_link():
    """
    Uses youtube-dl to fetch the direct link
    """
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
            retval = encode_data(get_key(), id=vid_id, title=title, url=retval, length=data['length'])
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
@record_request
def search():
    """
    Search youtube and return results
    """
    try:
        search_term = request.args.get('q')
        link = 'https://www.youtube.com/results?search_query=%s' % search_term
        link += '&sp=EgIQAQ%253D%253D'  # for only video
        link += '&gl=IN'
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
@record_request
def get_latest():
    """
    Get trending songs
    """
    try:
        max_count = int(request.args.get('number', '25'))
        if max_count <= 0:
            max_count = 1
        if max_count > 100:
            max_count = 100
    except ValueError:
        max_count = 25

    try:
        offset = int(request.args.get('offset', '0'))
        if offset < 0:
            offset = 0
        if offset > 100:
            offset = 100
    except ValueError:
        offset = 0

    type = request.args.get('type', 'popular')
    if type not in [_[0] for _ in trending_playlist]:
        type = 'popular'

    ret_vids = get_trending(type, max_count, offset=offset, get_url_prefix='/api/v1/g?url=')

    ret_dict = {
        'metadata': {
            'count': len(ret_vids),
            'type': type,
            'offset': offset
        },
        'results': ret_vids
    }

    return jsonify(ret_dict)


@app.route('/logs')
def get_log_page():
    """
    View application logs
    """
    user_key = request.args.get('key')

    if not user_key or user_key != get_key():
        return render_template('/unauthorized.html')

    try:
        offset = int(request.args.get('offset', '0'))
        if offset < 0:
            offset = 0
    except Exception:
        offset = 0

    try:
        number = int(request.args.get('number', '10'))
        if number < 1:
            number = 1
    except Exception:
        number = 0

    result = get_api_log(number, offset)

    if offset - number < 0:
        prev_link = None
    else:
        prev_link = '/logs?key={0}&number={1}&offset={2}'.format(
            user_key,
            number,
            offset - number
        )

    next_link = '/logs?key={0}&number={1}&offset={2}'.format(
        user_key,
        number,
        offset + number
    )

    day_path = result['day_path']
    day_sum = sum([x[1] for x in day_path])

    month_path = result['month_path']
    month_sum = sum([x[1] for x in month_path])

    all_path = result['all_path']
    all_sum = sum([x[1] for x in all_path])

    return render_template(
        '/log_page.html', logs=result['logs'], number=number, offset=offset, prev_link=prev_link, next_link=next_link,
        day_path=day_path, day_sum=day_sum, month_path=month_path, month_sum=month_sum, all_path=result['all_path'],
        all_sum=all_sum, popular_queries=result['popular_query']

    )


@app.route('/api/v1/playlists')
def get_playlists():
    count = len(trending_playlist)
    result = []
    for item in trending_playlist:
        result.append(
            {
                "playlist": item[0],
                "url": item[1]
            }
        )

    response = {
        'status': 200,
        'requestLocation': '/api/v1/playlists',
        "metadata": {
            "count": count
        },
        "results": result
    }

    return jsonify(response)


@app.route('/api/v1/stream')
@record_request
def stream():
    url = request.args.get('url')

    try:
        url = decode_data(get_key(), url)['url']
    except Exception:
        return 'Bad URL', 400

    def generate_data():
        r = requests.get(url, stream=True)
        for data_chunk in r.iter_content(chunk_size=2048):
            yield data_chunk

    return Response(generate_data(), mimetype='audio/mp4')
    # headers={'X-Content-Duration': 50}
