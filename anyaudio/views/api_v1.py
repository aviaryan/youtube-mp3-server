import traceback

import requests
from flask import Response

from anyaudio import logger
from flask import jsonify, request, render_template, url_for, make_response
from subprocess import check_output, call
from anyaudio import app, LOCAL

from anyaudio.helpers.search import get_videos, get_video_attrs, extends_length, get_suggestions, \
    get_search_results_html, make_search_api_response
from anyaudio.helpers.helpers import delete_file, get_ffmpeg_path, get_filename_from_title, \
    record_request, add_cover, get_download_link_youtube, make_error_response
from anyaudio.helpers.encryption import get_key, encode_data, decode_data
from anyaudio.helpers.data import trending_playlist
from anyaudio.helpers.database import get_trending, get_api_log


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
        command = 'curl -o %s %s' % (m4a_path, url)
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
        retval = get_download_link_youtube(vid_id, 'm4a/bestaudio')
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
        return make_error_response(msg=str(e), endpoint='/api/v1/g')


@app.route('/api/v1/search')
@record_request
def search():
    """
    Search youtube and return results
    """
    try:
        search_term = request.args.get('q')
        raw_html = get_search_results_html(search_term)
        vids = get_videos(raw_html)
        ret_vids = []
        for _ in vids:
            temp = get_video_attrs(_, removeLongResult=True)
            if temp:
                temp['get_url'] = '/api/v1' + temp['get_url']
                temp['stream_url'] = '/api/v1' + temp['stream_url']
                temp['suggest_url'] = temp['get_url'].replace('/g?', '/suggest?', 1)
                ret_vids.append(temp)
        ret_dict = make_search_api_response(search_term, ret_vids, '/api/v1/search')
    except Exception as e:
        return make_error_response(msg=str(e), endpoint='/api/v1/search')

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

    _type = request.args.get('type', 'popular').split(',')

    ret_meta = {
        "count": max_count,
        "offset": offset,
        "type": ""
    }

    result_dict = {}
    for i in _type:
        if i in [_[0] for _ in trending_playlist]:
            ret_meta["type"] += i + ","
            result_dict[i] = get_trending(i, max_count, offset, get_url_prefix='/api/v1/g?url=')

    if len(ret_meta["type"]) > 0:
        ret_meta["type"] = ret_meta["type"][:-1]

    ret_dict = {
        'metadata': ret_meta,
        'results': result_dict
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
    stream_settings = {
        'lo': 'webm[abr<=64]/webm[abr<=80]/m4a[abr<=64]/[abr<=96]/m4a',
        'md': 'webm[abr>=64][abr<=96]/[abr>=64][abr<=96]/webm[abr>=96][abr<=128]/webm/m4a',
        'hi': 'webm/m4a'
    }
    try:
        req = decode_data(get_key(), url)
        vid_id = req['id']
        quality = req.get('quality', 'md')
        url = get_download_link_youtube(
            vid_id,
            stream_settings[quality]
        )
    except Exception as e:
        return make_error_response(msg=str(e), endpoint='api/v1/stream')
    return jsonify(
        status=200,
        url=url_for(
            'stream_handler',
            url=encode_data(get_key(), url=url)
        )
    )


@app.route('/api/v1/stream_handler')
@record_request
def stream_handler():
    url = request.args.get('url')

    try:
        url = decode_data(get_key(), url)['url']
    except Exception:
        return 'Bad URL', 400

    def generate_data():
        r = requests.get(url, stream=True)
        logger.info('Streaming.. %s (%s bytes)' % (
            r.headers.get('content-type'),
            r.headers.get('content-length')
        ))
        for data_chunk in r.iter_content(chunk_size=2048):
            yield data_chunk

    mime = 'audio/mp4'
    if url.find('mime=audio%2Fwebm') > -1:
        mime = 'audio/webm'
    return Response(generate_data(), mimetype=mime)


@app.route('/api/v1/suggest')
@record_request
def suggest_songs():

    try:
        url = request.args.get('url')

        decoded_data = decode_data(get_key(), url)

        vid_id = decoded_data["id"]

        vids = get_suggestions(vid_id)

        count = len(vids)

        return jsonify(
            {
                "status": 200,
                "request_location": "/api/v1/suggest",
                "metadate": {
                    "count": count
                },
                "results": vids
            }
        )

    except Exception as e:
        return make_error_response(msg=str(e), endpoint='/api/v1/suggest')
