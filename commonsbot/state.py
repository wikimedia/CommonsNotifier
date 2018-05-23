from commonsbot import mysql
from commonsbot.utils import get_nomination_page
from pprint import pprint, pformat
from datetime import datetime
import pywikibot
import mwparserfromhell


def split(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


class DeletionState(object):
    FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, file_name, type, state, time=None):
        self.file_name = file_name
        self.type = type
        self.state = str(state)
        self.time = time
        self.info_loaded = False
        self.discussion_page = None

    def age(self):
        if self.time is None:
            return 0
        delta = datetime.utcnow() - self.time
        return delta.total_seconds()

    def get_discussion_info(self, site):
        if self.info_loaded or self.type != 'discussion':
            return

        self.info_loaded = True
        page = pywikibot.Page(site, 'File:%s' % self.file_name)
        text = page.get()

        self.discussion_page = get_nomination_page(text)


class DeletionStateStore(object):
    BATCH_SIZE = 100

    def __init__(self, conn):
        self.conn = conn

    def refresh_state(self, files, type):
        (present, missing) = self.load_state(files, type)
        states = []
        for file in missing:
            states.append(DeletionState(file, type, 'new'))
        self.save_state(states)
        states.extend(present.values())
        return states

    def set_state(self, type, files, state):
        sql = """UPDATE commons_deletions
            SET state=%s WHERE deletion_type=%s AND title IN (
            """ + mysql.tuple_sql(files) + ')'
        params = (state, type) + tuple([file.file_name for file in files])
        mysql.query(self.conn, sql, params)

    def set_failure(self, type, files):
        sql = """UPDATE commons_deletions
            SET retries=retries + 1
            WHERE deletion_type=%s AND title IN (
            """ + mysql.tuple_sql(files) + ')'
        params = (type,) + tuple([f.file_name for f in files])
        mysql.query(self.conn, sql, params)

    def load_state(self, files, type):
        present = {}
        for c in split(files, self.BATCH_SIZE):
            present.update(self._state_batch(c, type))
        missing = []
        for file in files:
            if file not in present:
                missing.append(file)

        return present, missing

    def _state_batch(self, files, type):
        sql = """SELECT title, deletion_type, state, state_time
FROM commons_deletions
WHERE title IN (%s) AND deletion_type=%s""" % (mysql.tuple_sql(files), '%s')
        files.append(type)
        rows = mysql.query(self.conn, sql, files)
        result = {}
        for row in rows:
            (title, type, state, time) = row
            file = DeletionState(title, type, state, time)
            result[title] = file
        return result

    def save_state(self, states):
        print('Saving %d rows' % len(states))
        count = 0
        for chunk in split(states, self.BATCH_SIZE):
            sql = """INSERT INTO commons_deletions(title, deletion_type, state)
            VALUES %s""" % ', '.join(['(%s, %s, %s)'] * len(chunk))
            params = ()
            for state in chunk:
                params += (state.file_name, state.type, state.state)
            mysql.query(self.conn, sql, params)
            count += len(chunk)
            print('%d rows inserted' % count)
        self.conn.commit()
