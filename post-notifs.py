#!/usr/bin/python3
import os
from commonsbot import mysql, lists
from commonsbot.config import settings as config
from commonsbot.state import DeletionStateStore, DeletionState
from commonsbot.i18n import I18n
import pywikibot
from pywikibot.site import Namespace
from pprint import pprint
import mwparserfromhell

NOTIFS_PER_WIKI = 10

userdb = mysql.connect('userdb')
commons_db = mysql.connect('replica')
store = DeletionStateStore(userdb)
commons = pywikibot.Site('commons', 'commons')


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
    params = (file_pretty, file_pretty, discussion )
    body = i18n.get(msg) % params

    msg = 'message-summary-%s' % type
    summary = i18n.get(msg)
    return (header, body, summary)


def spam_notifications(type, site, title, files):
    if len(files) == 0:
        print('Attempted to post about 0 files to %s:%s' % (site, title))
        return

    i18n = I18n.factory(site.code)
    # Assumes we ever only care about mainspace
    title = 'Talk:' + title
    page = pywikibot.Page(site, title)
    try:
        text = page.get()
    except pywikibot.exceptions.NoPage:
        text = ''
    except pywikibot.IsRedirectPage:
        print('"%s" is a redirect, skipping' % title)
        return

    if not page.botMayEdit():
        return

    # TODO: support multifile messages?
    for file in files:
        file.get_discussion_info(commons)
        (header, body, summary) = get_messages(type, i18n, file)
        text += '\n\n== %s ==\n%s ~~~~\n' % (header, body)

    try:
        page.put(text, summary)
        print('Posted %d notifications to %s' % (len(files), title))
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

    wikis = {}
    for filename in lines:
        result = lists.global_file_usage(commons_db,
                                         filename,
                                         NOTIFS_PER_WIKI,
                                         Namespace.MAIN)

        # Rejigger the results into the wiki => page => [files] format
        for wiki, pages in result.items():
            if not wiki in wikis:
                wikis[wiki] = {}
            page_index = wikis[wiki]
            for page in pages:
                if not page in page_index:
                    page_index[page] = []
                page_index[page].append(filename)

    for wiki, pages in wikis.items():
        site = pywikibot.site.APISite.fromDBName(wiki)
        for page, files in pages.items():
            states = [file_states[name] for name in files]
            spam_notifications(type, site, page, states)

process_list('discussion')
process_list('speedy')
