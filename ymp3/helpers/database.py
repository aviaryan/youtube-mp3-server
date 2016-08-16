import sqlite3
from ymp3 import DATABASE_PATH

from ..helpers.data import table_creation_sql_statements


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    return conn, conn.cursor()


def init_database():
    conn, cursor = get_connection()

    for statement in table_creation_sql_statements:
        cursor.execute(statement)

    conn.commit()
    conn.close()


def save_trending_songs(playlist_name, songs):

    conn, cursor = get_connection()

    try:
        sql = 'insert into trending_songs values(?,?,?,?,?,?,?,?)'

        data = [
            (
                song['id'],
                song['title'],
                song['thumb'],
                song['uploader'],
                song['length'],
                song['views'],
                song['get_url'],
                playlist_name
            ) for song in songs
        ]

        cursor.executemany(sql, data)
        conn.commit()

    except Exception:
        pass
    conn.close()


def get_trending(type='popular', count=25, get_url_prefix=''):
    conn, cursor = get_connection()

    sql = 'select * from trending_songs where playlist_ = ? limit ?'

    rows = cursor.execute(sql, (type, count))

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
                'get_url': get_url_prefix + row[6]
            }
        )

    conn.close()

    return vids


def clear_trending(pl_name):
    conn, cur = get_connection()

    sql = 'delete from trending_songs where playlist_ = ?'

    cur.execute(sql, (pl_name,))

    conn.commit()
    conn.close()
