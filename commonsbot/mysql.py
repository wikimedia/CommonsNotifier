import pymysql
# from pywikibot import config2 as config, output
from pprint import pformat, pprint
from commonsbot.config import settings as user_config


def connect(connection_name):
    conf = user_config['db_connections'][connection_name]
    return pymysql.connect(conf['host'],
                           port=conf['port'],
                           db=conf['database'],
                           user=conf['user'],
                           passwd=conf['password'],
                           use_unicode=True)


def query(conn, sql, params=(), verbose=None):
    """
    Yield rows from a MySQL query.
    @param conn: database connection
    @type conn: oursql.Connection
    @param sql: MySQL query to execute
    @type sql: str
    @param params: input parametes for the query, if needed
    @type params: tuple
    @param verbose: if True, print query to be executed;
        if None, config.verbose_output will be used.
    @type verbose: None or bool
    @return: generator which yield tuples
    """
    print('query')
    if verbose is None:
        verbose = False  # config.verbose_output

    cursor = conn.cursor()
    if verbose:
        print('Executing query:\n%s' % sql)
        print('Parameters:\n%s' % pformat(params))
    # query = query.encode('utf-8')
    params = tuple(p for p in params)

    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)

    for row in cursor.fetchall():
        yield row

    cursor.close()


def tuple_sql(tuple):
    return ', '.join(['%s']*len(tuple))
