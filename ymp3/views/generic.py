from flask import render_template, Markup, request
from ymp3 import app, logger
from ymp3.helpers.helpers import record_request


@app.route('/lite')
@record_request
def home():
    return render_template('/home.html')


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
