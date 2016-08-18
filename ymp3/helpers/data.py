import os

trending_playlist = [
    ('popular', 'https://www.youtube.com/playlist?list=PLFgquLnL59alCl_2TQvOiD5Vgm1hCaGSI'),
    ('latest', 'https://www.youtube.com/playlist?list=PLFgquLnL59akA2PflFpeQG9L01VFg90wS'),
    ('weekly', 'https://www.youtube.com/playlist?list=PLFgquLnL59alW3xmYiWRaoz0oM3H17Lth'),
    ('electroic', 'https://www.youtube.com/playlist?list=PLFPg_IUxqnZNnACUGsfn50DySIOVSkiKI'),
    ('latin', 'https://www.youtube.com/playlist?list=PLcfQmtiAG0X-fmM85dPlql5wfYbmFumzQ'),
    ('pop', 'https://www.youtube.com/playlist?list=PLDcnymzs18LWrKzHmzrGH1JzLBqrHi3xQ'),
    ('trap', 'https://www.youtube.com/playlist?list=PLL4IwRtlZcbvbCM7OmXGtzNoSR0IyVT02'),
    ('hiphop', 'https://www.youtube.com/playlist?list=PLH6pfBXQXHEC2uDmDy5oi3tHW6X8kZ2Jo'),
    ('reggae', 'https://www.youtube.com/playlist?list=PLYAYp5OI4lRLf_oZapf5T5RUZeUcF9eRO'),
    ('altrock', 'https://www.youtube.com/playlist?list=PL47oRh0-pTouthHPv6AbALWPvPJHlKiF7'),
    ('rnb', 'https://www.youtube.com/playlist?list=PLFRSDckdQc1th9sUu8hpV1pIbjjBgRmDw'),
    ('country', 'https://www.youtube.com/playlist?list=PLvLX2y1VZ-tFJCfRG7hi_OjIAyCriNUT2'),
    ('poprock', 'https://www.youtube.com/playlist?list=PLr8RdoI29cXIlkmTAQDgOuwBhDh3yJDBQ'),
    ('asian', 'https://www.youtube.com/playlist?list=PL0zQrw6ZA60Z6JT4lFH-lAq5AfDnO2-aE'),
    ('mexican', 'https://www.youtube.com/playlist?list=PLXupg6NyTvTxw5-_rzIsBgqJ2tysQFYt5'),
    ('soul', 'https://www.youtube.com/playlist?list=PLQog_FHUHAFUDDQPOTeAWSHwzFV1Zz5PZ'),
    ('heavymetal', 'https://www.youtube.com/playlist?list=PLfY-m4YMsF-OM1zG80pMguej_Ufm8t0VC'),
    ('blues', 'https://www.youtube.com/playlist?list=PLWNXn_iQ2yrKzFcUarHPdC4c_LPm-kjQy'),
    ('christian', 'https://www.youtube.com/playlist?list=PLLMA7Sh3JsOQQFAtj1no-_keicrqjEZDm'),
    ('hardrock', 'https://www.youtube.com/playlist?list=PL9NMEBQcQqlzwlwLWRz5DMowimCk88FJk'),
    ('classical', 'https://www.youtube.com/playlist?list=PLVXq77mXV53-Np39jM456si2PeTrEm9Mj'),
    ('edm', 'https://www.youtube.com/playlist?list=PLUg_BxrbJNY5gHrKsCsyon6vgJhxs72AH'),
    ('qawwali', 'https://www.youtube.com/playlist?list=PLXYM8jyeq3cfzuIzL0x0rEYxuMCl3dRqh'),
    ('india', 'https://www.youtube.com/playlist?list=PLFgquLnL59alF0GjxEs0V_XFCe7LM3ReH')
]

user_agents = [
    'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Googlebot/2.1 (+http://www.google.com/bot.html)',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
    ' Ubuntu Chromium/49.0.2623.108 Chrome/49.0.2623.108 Safari/537.36',
    'Gigabot/3.0 (http://www.gigablast.com/spider.html)',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; pt-BR) AppleWebKit/533.3 '
    '(KHTML, like Gecko)  QtWeb Internet Browser/3.7 http://www.QtWeb.net',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/41.0.2228.0 Safari/537.36',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.2 (KHTML, '
    'like Gecko) ChromePlus/4.0.222.3 Chrome/4.0.222.3 Safari/532.2',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.4pre) '
    'Gecko/20070404 K-Ninja/2.1.3',
    'Mozilla/5.0 (Future Star Technologies Corp.; Star-Blade OS; x86_64; U; '
    'en-US) iNet Browser 4.7',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.13) '
    'Gecko/20080414 Firefox/2.0.0.13 Pogo/2.0.0.13.6866',
    'WorldWideweb (NEXT)'
]

table_creation_sqlite_statements = [
    '''create table if not exists trending_songs(id_ text, title_ text, thumb_ text, uploader_ text, length_ text, views_ text, get_url_ text, playlist_ text)''',
]

table_creation_psql_statements = [
    '''create table if not exists api_log(args VARCHAR(8192), access_route varchar(8192), base_url varchar(5120), path varchar(5120), method VARCHAR(4), user_agent varchar(256), request_time TIMESTAMP WITH TIME zone default now())''',
]

psql_data = {
    'db_name': 'ymp3',
    'username': os.environ.get('OPENSHIFT_POSTGRESQL_DB_USERNAME'),
    'password': os.environ.get('OPENSHIFT_POSTGRESQL_DB_PASSWORD'),
    'host': os.environ.get('OPENSHIFT_POSTGRESQL_DB_HOST'),
    'port': os.environ.get('OPENSHIFT_POSTGRESQL_DB_PORT')
}
