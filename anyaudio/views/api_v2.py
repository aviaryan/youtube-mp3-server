import traceback

from flask import jsonify, request
from anyaudio import app

from anyaudio.helpers.search import get_videos, get_video_attrs, \
    get_search_results_html, make_search_api_response
from anyaudio.helpers.helpers import record_request, make_error_response
from anyaudio.helpers.encryption import get_key, decode_data

from anyaudio.helpers.pafymodule import get_stream, get_download


@app.route('/api/v2/stream')
@record_request
def stream_v2():
    url = request.args.get('url')
    try:
        vid_id = decode_data(get_key(), url)['id']
        url = get_stream(vid_id)
        return jsonify(status=200, url=url)
    except Exception as e:
        return make_error_response(msg=str(e), endpoint='api/v2/stream')


@app.route('/api/v2/g')
@record_request
def get_link_v2():
    url = request.args.get('url')
    try:
        data = decode_data(get_key(), url)
        vid_id = data['id']
        retval = get_download(vid_id)
        return jsonify(status=200, url=retval)
    except Exception as e:
        return make_error_response(msg=str(e), endpoint='/api/v2/g')


@app.route('/api/v2/search')
@record_request
def search_v2():
    try:
        search_term = request.args.get('q')
        raw_html = get_search_results_html(search_term)
        vids = get_videos(raw_html)
        ret_vids = []
        for _ in vids:
            temp = get_video_attrs(_, removeLongResult=False)
            if temp:
                temp['get_url'] = '/api/v2' + temp['get_url']
                temp['stream_url'] = '/api/v2' + temp['stream_url']
                temp['suggest_url'] = temp['get_url'].replace('v2/g?', 'v1/suggest?', 1)
                ret_vids.append(temp)
        ret_dict = make_search_api_response(search_term, ret_vids, '/api/v2/search')
    except Exception as e:
        return make_error_response(msg=str(e), endpoint='/api/v2/search')

    return jsonify(ret_dict)
