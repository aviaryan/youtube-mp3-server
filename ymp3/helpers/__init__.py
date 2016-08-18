import psycopg2.pool
from data import psql_data

psql_connection_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=10,
    maxconn=100,
    dsn=psql_data['dsn']
)
