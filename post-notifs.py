#!/usr/bin/python3
import os
from commonsbot import mysql, config
from commonsbot.state import DeletionStateStore, DeletionState
from commonsbot.i18n import I18n
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
    header = i18n.get(msg)

    msg = 'message-body-%s' % type
    if type == 'discussion':
        discussion = file.discussion_page
        if discussion is None:
            discussion = 'File:%s' % file_pretty
        discussion = 'Commons:Deletion requests/%s' % discussion
    else:
        discussion = 'File:%s' % file_pretty
    params = (file_pretty, file_pretty, discussion)
    body = i18n.get(msg) % params

    msg = 'message-summary-%s' % type
    summary = i18n.get(msg)
    return (header, body, summary)


def spam_notifications(type, page, file, state):
    i18n = I18n.factory(page.site.code)
    # Assumes we ever only care about mainspace
    talk_page = page.toggleTalkPage()
    try:
        text = talk_page.get()
    except pywikibot.exceptions.NoPage:
        text = ''
    except pywikibot.IsRedirectPage:
        print('"%s" is a redirect, skipping' % talk_page.title())
        return

    if not talk_page.botMayEdit():
        return

    # TODO: support multifile messages?
    state.get_discussion_info(commons)
    (header, body, summary) = get_messages(type, i18n, state)
    text += '\n\n== %s ==\n%s ~~~~\n' % (header, body)

    try:
        talk_page.put(text, summary)
        print('Posted a notification about %s to %s' %
              (file.title(), talk_page.title()))
    except:
        pass


def process_list(type):
    """
    Processes a list of files to notify about

    @type type: str
    """
    filename = 'lists/%s.txt' % type
    if not os.path.isfile(filename) or not os.path.exists(filename):
        return
    file = open(filename, 'r')
    lines = [s.strip() for s in file.readlines()]
    file.close()

    (file_states, _) = store.load_state(lines, type)

    for filename in lines:
        file = FilePage(commons, filename)
        pageset = file.globalusage(MAX_GLOBALUSAGE)

        for usage in pageset:
            # Rejigger the results into the wiki => page => [files] format
            wiki = usage.site.dbName()
            if wiki not in config.wikis:
                continue
            if usage.namespace() != Namespace.MAIN:
                continue

            if filename in file_states:
                state = file_states[filename]
            else:
                print('No deletion state found for %s, stubbing' % filename)
                state = DeletionState(filename, type, 'new')
            spam_notifications(type, usage, file, state)


process_list('discussion')
# process_list('speedy')
