from commonsbot import mysql
from pywikibot.site import Namespace


def page_to_str(tuple):
    return '%d:%s' % tuple


def category_listing(conn, name, type=None, namespaces=()):
    params = (name,)
    sql = """SELECT page_namespace, page_title
FROM categorylinks, page
WHERE cl_from=page_id AND cl_to=%s"""

    if type is not None:
        params += (type,)
        sql += ' AND cl_type=%s'

    if namespaces:
        for i in range(len(namespaces)):
            params += (str(namespaces[i]),)
        sql += ' AND page_namespace IN (%s)' % mysql.tuple_sql(namespaces)

    return mysql.query(conn, sql, params)


class RecursiveCategoryScanner(object):

    """
    Performs a recursive category members scan
    """

    def __init__(self, conn):
        self.conn = conn

    def scan(self, category, depth, namespaces=()):
        self.categories = set()
        self.pages = {}
        self.namespaces = namespaces
        self.query_namespaces = namespaces
        if len(namespaces) > 0 and not (Namespace.CATEGORY in namespaces):
            self.query_namespaces += (Namespace.CATEGORY,)
        self._recurse(category, depth)
        return [v for _, v in iter(self.pages.values())]

    def _recurse(self, category, depth):
        if depth <= 0:
            return
        if category in self.categories:
            raise RuntimeError(
                'Trying to recurse through an already recursed category')

        self.categories.add(category)
        pages = category_listing(self.conn,
                                 category,
                                 namespaces=self.query_namespaces)
        for page in pages:
            (ns, title) = page
            if not self.namespaces or ns in self.namespaces:
                self.pages[page_to_str(page)] = page

            if ns == Namespace.CATEGORY and title not in self.categories:
                self._recurse(title, depth - 1)
