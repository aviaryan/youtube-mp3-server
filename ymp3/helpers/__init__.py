import psycopg2.pool
from data import psql_data

psql_connection_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=10,
    maxconn=100,
    database=psql_data['db_name'],
    user=psql_data['username'],
    password=psql_data['password'],
    host=psql_data['host'],
    port=psql_data['port']
)
