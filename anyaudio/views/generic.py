from flask import redirect
from flask import render_template, Markup, request
from flask import url_for

from anyaudio import app
from anyaudio.helpers.encryption import encode_data, get_key
from anyaudio.helpers.helpers import record_request, get_download_link_youtube
from anyaudio.helpers import database
from anyaudio.helpers.search import get_search_results_html, get_videos, \
    get_video_attrs, get_suggestions


@app.route('/lite', strict_slashes=False)
@record_request
def home():
    popular_searches = database.get_popular_searches(number=50)
    return render_template('/home.html', searches=popular_searches)


@app.route('/lite/search')
@record_request
def lite_search():
    search_term = request.args.get('q', None)
    if search_term is None:
        return redirect('/lite')
    raw_html = get_search_results_html(search_term)
    vids = get_videos(raw_html)
    ret_vids = []
    for _ in vids:
        temp = get_video_attrs(_, removeLongResult=True)
        if temp:
            temp['get_url'] = '/api/v1' + temp['get_url']
            temp['stream_url'] = '/api/v1' + temp['stream_url']
            temp['suggest_url'] = temp['get_url'].replace('/g?', '/suggest?',
                                                          1)
            ret_vids.append(temp)
    return render_template('/lite_search.html', results=ret_vids,
                           term=search_term)


@app.route('/lite/music/<id>')
@record_request
def serve_music_lite(id):
    video = {}
    url = get_download_link_youtube(
        id, 'webm[abr<=64]/webm[abr<=80]/m4a[abr<=64]/[abr<=96]/m4a')
    stream_url = url_for('stream_handler', url=encode_data(get_key(), url=url))
    url = get_download_link_youtube(id, 'm4a/bestaudio')
    download_url = url_for('download_file', url=encode_data(get_key(), url=url))
    video['stream_url'] = stream_url
    video['download_url'] = download_url
    video['suggestions'] = get_suggestions(id)
    return render_template('/lite_song.html', video=video)


@app.route('/beta')
@app.route('/')
@record_request
def home_beta():
    return render_template('/index.html')


@app.route('/terms-of-use')
@record_request
def terms_of_use():
    return render_template('/terms-of-use.html')


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


@app.route('/app')
@record_request
def download_app():
    return render_template('/app.html')


@app.route('/robots.txt')
def get_robots():
    return render_template("robots.txt"), 200, {'Content-Type': 'text/text; charset=utf-8'}
