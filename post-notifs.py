#!/usr/bin/python3
import os, sys
from commonsbot import mysql, config
from commonsbot.state import DeletionStateStore, DeletionState
from commonsbot.i18n import I18n
from commonsbot.utils import PerWikiCounter
import pywikibot
from pywikibot import Site, Page, FilePage
from pywikibot.site import Namespace
from pprint import pprint

NOTIFS_PER_WIKI = 10
MAX_GLOBALUSAGE = 1000

userdb = mysql.connect('userdb')
store = DeletionStateStore(userdb)
commons = Site('commons', 'commons')


def get_messages(type, i18n, file):
    file_pretty = file.file_name.replace('_', ' ')

    msg = 'message-header-%s' % type
    header = i18n.msg(msg)

    msg = 'message-body-%s' % type
    if type == 'discussion':
        discussion = file.discussion_page
        if discussion is None:
            discussion = 'File:%s' % file_pretty
        discussion = 'Commons:Deletion requests/%s' % discussion
        params = (file_pretty, discussion)
    else:
        discussion = 'File:%s' % file_pretty
        params = (file_pretty,)
    body = i18n.msg(msg, params)

    msg = 'message-summary-%s' % type
    summary = i18n.msg(msg)
    return (header, body, summary)


def spam_notifications(type, talk_page, file, state):
    i18n = I18n.factory(talk_page.site.code)

    try:
        text = talk_page.get()
    except pywikibot.exceptions.NoPage:
        text = ''

    try:
        state.get_discussion_info(commons)
    except:
        ex = sys.exc_info()[0]
        print('%s getting file info, skipping: %s' % (type(ex).__name__, str(ex)),
              file=sys.stderr)
        return False

    # TODO: support multifile messages?
    (header, body, summary) = get_messages(type, i18n, state)
    talk_page.text += '\n\n== %s ==\n%s ~~~~\n' % (header, body)

    if config.dry_run:
        print('DRY RUN: not posting about %s to %s' % (file, talk_page))
        return True

    talk_page.save(summary=summary, botflag=True, tags='bot trial')
    print('Posted a notification about %s to %s' %
            (file, talk_page))

    return True


def process_list(type):
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

    wikis = PerWikiCounter(NOTIFS_PER_WIKI)
    for filename in lines:
        ok = False
        file = FilePage(commons, filename)
        pageset = file.globalusage(MAX_GLOBALUSAGE)
        if filename in file_states:
            state = file_states[filename]
        else:
            print('No deletion state found for %s, stubbing' % filename)
            state = DeletionState(filename, type, 'new')

        for usage in pageset:
            wiki = usage.site.dbName()
            if wiki not in config.wikis:
                continue
            if usage.namespace() != Namespace.MAIN:
                continue

            talk_page = usage.toggleTalkPage()
            if talk_page.isRedirectPage():
                continue
            if not talk_page.botMayEdit():
                continue
            if talk_page.exists() and not talk_page.canBeEdited():
                continue
            if not wikis.next(wiki, filename):
                continue

            ok = ok or spam_notifications(type, talk_page, file, state)

        if ok:
            store.set_state(type, [state], 'notified')
        else:
            store.set_failure(type, [state])


process_list('discussion')
process_list('speedy')
