import re
from encryption import get_key, encode_data
from .networking import open_page

INF = float("inf")


def get_videos(html):
    """
    separate videos in html
    """
    first = html.find('yt-lockup-tile')
    html = html[first + 2:]
    vid = []
    while True:
        pos = html.find('yt-lockup-tile')
        if pos == -1:
            pos = INF
            vid.append(html)
            break
        vid.append(html[:pos + 2])
        html = html[pos + 3:]
    return vid


def get_video_attrs(html):
    """
    get video attributes from html
    """
    result = {}
    # get video id and description
    regex = 'yt\-lockup\-title.*?href.*?watch\?v\=(.*?[^\"]+)'
    regex += '.*? title\=\"(.*?[^\"]+)'
    temp = re.findall(regex, html)
    if len(temp) and len(temp[0]) == 2:
        result['id'] = temp[0][0]
        result['title'] = temp[0][1]
    # length
    length_regex = 'video\-time.*?\>([^\<]+)'
    temp = re.findall(length_regex, html)
    if len(temp) > 0:
        result['length'] = temp[0].strip()
    # uploader
    upl_regex = 'yt\-lockup\-byline.*?\>.*?\>([^\<]+)'
    temp = re.findall(upl_regex, html)
    if len(temp) > 0:
        result['uploader'] = temp[0].strip()
    # time ago
    time_regex = 'yt\-lockup\-meta\-info.*?\>.*?\>([^\<]+).*?([0-9\,]+)'
    temp = re.findall(time_regex, html)
    if len(temp) and len(temp[0]) == 2:
        result['time'] = temp[0][0]
        result['views'] = temp[0][1]
    # thumbnail
    if 'id' in result:
        thumb = 'http://img.youtube.com/vi/%s/0.jpg' % result['id']
        result['thumb'] = thumb
    else:
        return None
    # Description
    desc_regex = 'yt-lockup-description.*?>(.*?)<'
    temp = re.findall(desc_regex, html)
    if len(temp) > 0:
        result['description'] = temp[0]
    else:
        result['description'] = ''

    # check if all items present. If not present, usually some problem in parsing
    if len(result) != 8:
        return None
    # check length
    if extends_length(result['length'], 20 * 60):
        return None
    # return
    result['get_url'] = '/g?url=' + encode_data(
        get_key(), id=result['id'],
        title=result['title'], length=result['length']
    )
    result['stream_url'] = result['get_url'].replace('/g?', '/stream?', 1)
    return result


def extends_length(length, limit):
    """
    Return True if length more than limit
    """
    try:
        metrics = [int(i.strip()) for i in length.split(':')]
        secs = 0
        for metric in metrics:
            secs = 60 * secs + metric
        return (secs > limit)
    except Exception:
        return True


def get_suggestions(vid_id, get_url_prefix='/api/v1'):
    url = "https://www.youtube.com/watch?v=" + vid_id
    raw_html = open_page(url)

    area_of_concern_regex = r'<div class=\"watch-sidebar-section\"(.*?)<div id=\"watch7-hidden-extras\"'
    area_of_concern = ' '.join(re.findall(area_of_concern_regex, raw_html, re.DOTALL))

    videos_html_regex = r'class=\"video-list-item.*?a href=\"/watch\?v=(.*?)\" class.*? class=\"title.*?>(.*?)</span>' \
                        r'.*?Duration: (.*?)\..*?<span class=\"g-hovercard.*?>(.*?)</span>.*?view-count\">(.*?) ' \
                        r'views.*?<li '
    videos_html = re.findall(videos_html_regex, area_of_concern, re.DOTALL)

    ret_list = []
    for video in videos_html:
        _id = video[0]
        title = video[1].strip('\n\t ')
        duration = video[2]
        uploader = video[3]
        views = video[4]
        get_url = get_url_prefix + '/g?url=' + encode_data(get_key(), id=_id, title=title, length=duration)
        stream_url = get_url.replace('/g?', '/stream?', 1)
        suggest_url = get_url.replace('/g?', '/suggest?', 1)

        if extends_length(duration, 20*60):
            continue

        ret_list.append(
            {
                "id": _id,
                "title": title,
                "length": duration,
                "uploader": uploader,
                "thumb": 'http://img.youtube.com/vi/%s/0.jpg' % _id,
                "get_url": get_url,
                "stream_url": stream_url,
                "views": views,
                "suggest_url": suggest_url
            }
        )

    return ret_list
