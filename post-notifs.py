#!/usr/bin/python3
import os, sys
from commonsbot import mysql, config
from commonsbot.state import DeletionStateStore, DeletionState
from commonsbot.i18n import I18n
from commonsbot.utils import PerWikiMapper
from commonsbot.formatters import SpeedyFormatter, DiscussionFormatter
import pywikibot
from pywikibot import Site, Page, FilePage
from pywikibot.site import Namespace


NOTIFS_PER_WIKI = 10
MAX_GLOBALUSAGE = 10000


userdb = mysql.connect('userdb')
store = DeletionStateStore(userdb)
commons = Site('commons', 'commons')


def spam_notifications(notif_type, formatter_class, talk_page, files):
    i18n = I18n.factory(talk_page.site.code)

    try:
        text = talk_page.get()
    except pywikibot.exceptions.NoPage:
        text = ''

    formatter = formatter_class(i18n)
    talk_page.text = text + formatter.format(files)
    summary = formatter.format_summary()

    if config.dry_run:
        print('DRY RUN: not posting about %d %s files to %s' % (len(files), notif_type, talk_page))
        return True

    talk_page.save(summary=summary, botflag=True, tags='bot trial')
    print('Posted a notification about %d %s files to %s' % (len(files), notif_type, talk_page))

    return True


def process_list(type, formatter_class):
    """
    Processes a list of files to notify about

    @type type: str
    """
    filename = 'lists/%s.txt' % type
    if not os.path.isfile(filename) or not os.path.exists(filename):
        return
    file = open(filename, 'r', encoding='utf8')
    lines = [s.strip() for s in file.readlines()]
    file.close()

    (file_states, _) = store.load_state(lines, type)
    mapper = PerWikiMapper(NOTIFS_PER_WIKI)
    notified_files = set()

    for filename in lines:
        file = FilePage(commons, filename)
        if filename in file_states:
            state = file_states[filename]
        else:
            print('No deletion state found for %s, stubbing' % filename,
                file=sys.stderr)
            state = DeletionState(filename, type, 'new')
            file_states[filename] = state
        state.file_page = file
        if type == 'discussion':
            state.load_discussion_info(commons)

        pageset = file.globalusage(MAX_GLOBALUSAGE)
        for page in pageset:
            wiki = page.site.dbName()
            if wiki not in config.wikis:
                continue
            if page.namespace() != Namespace.MAIN:
                continue

            talk_page = page.toggleTalkPage()
            if talk_page.isRedirectPage():
                continue
            if not talk_page.botMayEdit():
                continue
            if talk_page.exists() and not talk_page.canBeEdited():
                continue
            mapper.add(filename, page)

    for page, files in mapper.files_per_page():
        states = []
        for filename in files:
            state = file_states[filename]
            states.append(state)

        try:
            spam_notifications(type, formatter_class, page.toggleTalkPage(), states)
        except:
            # Error - save state to avoid reposting and then rethrow
            failed = set(states)
            failed_only = failed - notified_files
            store.set_failure(type, list(failed_only))
            store.set_state(type, list(notified_files), 'notified')
            userdb.commit()
            raise

        notified_files.update(states)

    store.set_state(type, list(notified_files), 'notified')
    userdb.commit()


process_list('discussion', DiscussionFormatter)
process_list('speedy', SpeedyFormatter)
store.expire_failed()
userdb.commit()
