import pymysql
# from pywikibot import config2 as config, output
from pprint import pformat, pprint
from commonsbot import config


def decode_tuple(tuple):
    result = ()
    for var in tuple:
        if isinstance(var, bytes):
            var = var.decode('utf8')
        result += (var,)
    return result


def connect():
    return pymysql.connect(read_default_file=config.mysql_config_file,
                           charset='utf8',
                           use_unicode=True)


def query(conn, sql, params=(), verbose=None):
    """
    Yield rows from a MySQL query.
    @param conn: database connection
    @type conn: pymysql.Connection
    @param sql: MySQL query to execute
    @type sql: str
    @param params: input parametes for the query, if needed
    @type params: tuple
    @param verbose: if True, print query to be executed;
        if None, config.verbose_output will be used.
    @type verbose: None or bool
    @return: generator which yield tuples
    """
    if verbose is None:
        verbose = False  # config.verbose_output

    cursor = conn.cursor()
    if verbose:
        print('Executing query:\n%s' % sql)
        print('Parameters:\n%s' % pformat(params))
    params = tuple(p for p in params)

    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)

    result = [decode_tuple(row) for row in cursor.fetchall()]
    cursor.close()
    return result


def tuple_sql(tuple):
    return ', '.join(['%s']*len(tuple))
