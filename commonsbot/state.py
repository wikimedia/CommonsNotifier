from commonsbot import mysql
from commonsbot.utils import get_nomination_page
from pprint import pprint, pformat
from datetime import datetime
import pywikibot
import mwparserfromhell
import sys


def split(l, n):
    """
    Splits a list into several lists of given size

    @param l: List to split
    @type l: list
    @param n: Maximum sublist size
    @type n: int
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]


class DeletionState(object):
    """
    Represents a single file nominated for deletion
    """

    FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, file_name, type, state, time=None):
        """
        @param file_name: Name of file
        @type file: str
        @param type: Deletion type
        @param state: Where are we with informing about this file?
        @type state: str
        @param time: When we first saw this file, use current time if none
        @type time: datetime.datetime|None
        """
        self.file_name = file_name
        self.type = type
        self.state = str(state)
        self.time = time
        self.info_loaded = False
        self.discussion_page = None
        self.file_page = None

    def age(self):
        """
        Time since we first saw this file in seconds

        @rtype
        """
        if self.time is None:
            return 0
        delta = datetime.utcnow() - self.time
        return delta.total_seconds()

    def load_discussion_info(self, site):
        """
        Loads deletion discussion page information into this object's discussion_page property
        """
        if self.info_loaded or self.type != 'discussion':
            return

        self.info_loaded = True
        if self.discussion_page is None:
            page = pywikibot.Page(site, 'File:' + self.file_name)
        else:
            page = self.discussion_page

        text = page.text

        discussion = get_nomination_page(text)
        if discussion is None:
            print("Can't retrieve a discussion page for %s, guessing" %
                  self.file_name, file=sys.stderr)
            discussion = 'File:' + self.file_name
        discussion = 'Commons:Deletion requests/' + discussion

        self.discussion_page = discussion


class DeletionStateStore(object):
    """
    Operates a database store for DeletionState objects
    """
    BATCH_SIZE = 100
    MAX_FAILURES = 3

    def __init__(self, conn):
        """
        @param conn: Database connection
        @type conn: pymysql.Connection
        """
        self.conn = conn

    def refresh_state(self, files, type):
        """
        Loads information about given files, creating records for those that aren't yet in the DB

        @param files: List of file names as strings
        @type files: list
        @param type: Deletion type
        @type type: str
        @rtype: list
        """
        (present, missing) = self.load_state(files, type)
        states = []
        for file in missing:
            states.append(DeletionState(file, type, 'new'))
        self.save_state(states)
        states.extend(present.values())
        return states

    def set_state(self, type, files, state):
        """
        Sets states for the given files

        @param type: Deletion type
        @type type: str
        @param files: List of DeletionState objects
        @type files: list
        @param state: File state
        @type state: str
        """
        if not files:
            return
        sql = """UPDATE commons_deletions
            SET state=%s WHERE deletion_type=%s AND title IN (
            """ + mysql.tuple_sql(files) + ')'
        params = (state, type) + tuple([file.file_name for file in files])
        mysql.query(self.conn, sql, params)

    def set_failure(self, type, files):
        """
        Increments failure counters for the given files

        @param type: Deletion type
        @type type: str
        @param files: List of DeletionState objects
        @type files: list
        """
        if not files:
            return
        sql = """UPDATE commons_deletions
            SET retries=retries + 1
            WHERE deletion_type=%s AND title IN (""" + mysql.tuple_sql(files) + ')'
        params = (type,) + tuple([f.file_name for f in files])
        mysql.query(self.conn, sql, params)

    def load_state(self, files, type):
        """
        Loads state for the given files and returns lists of files present in the DB and missing from it

        @param files: List of files as strings
        @type files: list
        @param type: Deletion type
        @type type: str
        @rtype: list, list
        """
        present = {}
        for c in split(files, self.BATCH_SIZE):
            present.update(self._state_batch(c, type))
        missing = []
        for file in files:
            if file not in present:
                missing.append(file)

        return present, missing

    def expire_failed(self):
        """
        Marks files with error counters exceeding MAX_FAILURES as failed
        """
        sql = """UPDATE commons_deletions SET state='failed', state_time=now()
            WHERE state='new' AND retries > %s
            """
        mysql.query(self.conn, sql, (self.MAX_FAILURES,))

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
        """
        Saves information about the given files

        @param states: List of DeletionState objects
        @type states: list
        """
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
