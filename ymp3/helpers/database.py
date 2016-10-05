import json
import sqlite3
from ymp3 import DATABASE_PATH
from . import psql_connection_pool

from ..helpers.data import table_creation_sqlite_statements, table_creation_psql_statements


def init_databases():
    init_sqlite_database()
    init_psql_database()


def get_sqlite_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    return conn, conn.cursor()


def init_sqlite_database():
    conn, cursor = get_sqlite_connection()

    for statement in table_creation_sqlite_statements:
        cursor.execute(statement)

    conn.commit()
    conn.close()


def init_psql_database():
    conn = psql_connection_pool.getconn()
    cur = conn.cursor()

    for statement in table_creation_psql_statements:
        cur.execute(statement)

    conn.commit()
    psql_connection_pool.putconn(conn)


def save_trending_songs(playlist_name, songs):
    conn, cursor = get_sqlite_connection()

    try:
        sql = 'insert into trending_songs values(?,?,?,?,?,?,?,?,?)'

        data = [
            (
                song['id'],
                song['title'],
                song['thumb'],
                song['uploader'],
                song['length'],
                song['views'],
                song['get_url'],
                playlist_name,
                song['description'].decode('utf-8')
            ) for song in songs
        ]

        cursor.executemany(sql, data)
        conn.commit()

    except Exception:
        import traceback
        traceback.print_exc()
        pass
    conn.close()


def get_trending(type='popular', count=25, offset=0, get_url_prefix=''):
    conn, cursor = get_sqlite_connection()

    sql = 'select * from trending_songs where playlist_ = ? limit ? offset ?'

    rows = cursor.execute(sql, (type, count, offset))

    vids = []
    for row in rows:
        vids.append(
            {
                'id': row[0],
                'title': row[1],
                'thumb': row[2],
                'uploader': row[3],
                'length': row[4],
                'views': row[5],
                'get_url': get_url_prefix + row[6],
                'stream_url': (get_url_prefix + row[6]).replace('/g?', '/stream?', 1),
                'description': row[8]
            }
        )

    conn.close()

    return vids


def clear_trending(pl_name):
    conn, cur = get_sqlite_connection()

    sql = 'delete from trending_songs where playlist_ = ?'

    cur.execute(sql, (pl_name,))

    conn.commit()
    conn.close()


def log_api_call(obj):
    con = psql_connection_pool.getconn()
    cur = con.cursor()

    sql = "insert into api_log values(%s, %s, %s, %s, %s, %s)"

    args = json.dumps(dict(obj.args))
    access_route = json.dumps(list(obj.access_route))
    base_url = obj.base_url
    path = obj.path
    method = obj.method
    useragent = str(obj.user_agent)

    cur.execute(
        sql,
        (args, access_route, base_url, path, method, useragent)
    )

    con.commit()

    psql_connection_pool.putconn(con)


def get_api_log(number=10, offset=0):
    sql_logs = '''select args, access_route, base_url, path, method, user_agent, request_time at time zone 'IST'
    from api_log where user_agent <> \'Ruby\' order by request_time desc limit %s offset %s'''

    sql_day_path = '''select t1.path, count(*) from
    (select path from api_log where
    (extract(epoch from current_timestamp) -
    extract(epoch from request_time))/60/60/24 <= 1)
     as t1 group by t1.path;'''

    sql_month_path = '''select t1.path, count(*) from
    (select path from api_log where
    (extract(epoch from current_timestamp) -
    extract(epoch from request_time))/60/60/24/30 <= 1)
     as t1 group by t1.path;'''

    sql_all_path = '''select path, count(*) from api_log group by path;'''

    sql_popular_query = '''select * from (select q[1] as query, count(*) as cnt from
(select regexp_matches(args, 'q": \[\"(.*)\"') as q, request_time from api_log where
 path like '/api/v_/search') as d where (extract(epoch from CURRENT_TIMESTAMP ) -
 extract(epoch from request_time))/60/60/24 <= 1 group by q[1]) t2 order by cnt desc limit 9;'''

    con = psql_connection_pool.getconn()
    cur = con.cursor()

    cur.execute(sql_logs, (number, offset))
    rows_calls = cur.fetchall()

    cur.execute(sql_day_path)
    rows_day_path = cur.fetchall()

    cur.execute(sql_month_path)
    rows_month_path = cur.fetchall()

    cur.execute(sql_popular_query)
    rows_popular_query = cur.fetchall()

    cur.execute(sql_all_path)
    rows_all_path = cur.fetchall()

    calls = []
    for row in rows_calls:
        calls.append(
            {
                'args': row[0],
                'access_route': row[1],
                'base_url': row[2],
                'path': row[3],
                'method': row[4],
                'user_agent': row[5],
                'request_time': row[6]
            }
        )

    psql_connection_pool.putconn(con)
    return {
        'logs': calls,
        'day_path': rows_day_path,
        'month_path': rows_month_path,
        'all_path': rows_all_path,
        'popular_query': rows_popular_query
    }
