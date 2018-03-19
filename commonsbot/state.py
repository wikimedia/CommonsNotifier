from commonsbot import mysql
from pprint import pprint, pformat


def split(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


class DeletionState(object):
    def __init__(self, file_name, type, state):
        self.file_name = file_name
        self.type = type
        self.state = state


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

    def load_state(self, files, type):
        present = {}
        mysql.query(self.conn, 'SHOW TABLES')
        for c in split(files, self.BATCH_SIZE):
            present.update(self._state_batch(c, type))
        missing = []
        for file in files:
            if file not in present:
                missing.append(file)

        return present, missing

    def _state_batch(self, files, type):
        sql = """SELECT title, deletion_type, state, touched
FROM commons_deletions
WHERE title IN (%s) AND deletion_type=%s""" % (mysql.tuple_sql(files), '%s')
        files.append(type)
        rows = mysql.query(self.conn, sql, files)
        result = {}
        for row in rows:
            (title, type, state, touched) = row
            file = DeletionState(title, type, state)
            file.touched = touched
            result[title] = file
        return result

    def save_state(self, states):
        print('Saving %d rows' % len(states))
        for state in states:
            print('row')
            sql = """INSERT INTO commons_deletions(title, deletion_type, state)
    VALUES (%s, %s, %s)"""
            params = (state.file_name, state.type, state.state)
            mysql.query(self.conn, sql, params, verbose=True)
