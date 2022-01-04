#!/usr/bin/python3
import os
import sys
from commonsbot import mysql, config
from commonsbot.state import DeletionStateStore, DeletionState
from commonsbot.i18n import I18n, language_has_all_messages, MessageNotFound
from commonsbot.utils import PerWikiMapper, check_already_posted
from commonsbot.formatters import SpeedyFormatter, DiscussionFormatter, NoPermissionFormatter
import pywikibot
from pywikibot import Site, Page, FilePage
from pywikibot.site import Namespace


NOTIFS_PER_WIKI = 10
MAX_GLOBALUSAGE = 10000


commons = Site('commons', 'commons')


def with_store(callback):
    """
    Wraps operations on database into open/save to prevent connections from timing out

    @param callback: Function to be called that receives a DeletionStateStore object as a parameter
    @type callback: function
    """
    userdb = mysql.connect()
    store = DeletionStateStore(userdb)
    callback(store)
    userdb.commit()
    userdb.close()


def spam_notifications(notif_type, formatter_class, talk_page, files):
    """
    Posts a notification to the talk page

    @param notif_type: Notification type
    @type notif_type: str
    @param formatter_class: Class to be used for formatting messages
    @type formatter_class: commonsbot.formatters.Formatter
    @param talk_page: Page to post to
    @type talk_page: pywikibot.Page
    @param files: A list of DeletionState objects to report
    @type files: list
    """
    assert len(files) > 0

    wiki_options = config.for_wiki(talk_page.site.dbName())

    if notif_type not in wiki_options['notification_types']:
        return

    lang_code = wiki_options['language']
    if lang_code is None:
        lang_code = talk_page.site.code
    # if not language_has_all_messages(lang_code):
    #     return
    i18n = I18n.factory(lang_code)

    try:
        text = talk_page.get()
    except pywikibot.exceptions.NoPageError:
        text = ''

    ourlist = []
    for file in files:
        if check_already_posted(text, file.file_name, notif_type):
            print('%s has already been notified about %s, skipping' % (talk_page, file.file_name), file=sys.stderr)
        else:
            ourlist.append(file)

    if len(ourlist) == 0:
        print('Nothing to report about at %s' % talk_page, file=sys.stderr)
        return

    ourlist.sort(key=lambda file: file.file_name)

    try:
        formatter = formatter_class(i18n)
        talk_page.text = text + formatter.format(ourlist)
        summary = formatter.format_summary()
    except MessageNotFound as e:
        print(str(e), file=sys.stderr)
        return

    if config.dry_run:
        print('DRY RUN: not posting about %d %s files to %s' % (len(ourlist), notif_type, talk_page))
        return

    kvargs = {}
    if wiki_options['tags'] is not None:
        kvargs['tags'] = wiki_options['tags']
    try:
        talk_page.save(summary=summary, botflag=wiki_options['markasbot'], minor=wiki_options['minoredit'], **kvargs)
        print('Posted a notification about %d %s files to %s' % (len(ourlist), notif_type, talk_page))
    except pywikibot.LockedPage:
        print('Page %s is protected, skipping' % talk_page, file=sys.stderr)


def process_list(type, formatter_class):
    """
    Post notifications about a certain type of deletions

    @param type: Deletion type
    @type type: str
    @param formatter_class: Class to be used for formatting messages
    @type formatter_class: commonsbot.formatters.Formatter
    """
    filename = 'lists/%s.txt' % type
    if not os.path.isfile(filename) or not os.path.exists(filename):
        return
    file = open(filename, 'r', encoding='utf8')
    lines = [s.strip() for s in file.readlines()]
    file.close()

    file_states = {}

    def load(store):
        nonlocal file_states
        (file_states, _) = store.load_state(lines, type)

    with_store(load)
    mapper = PerWikiMapper(NOTIFS_PER_WIKI)
    notified_files = set()

    for filename in lines:
        file = FilePage(commons, filename)

        if not file.exists():
            print('File:%s missing, skipping.' % filename, file=sys.stderr)
            continue

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
            page = Page(commons, state.discussion_page)
            if not page.exists():
                print("Discussion page %s doesn't exist, not notifying about this file" % page, file=sys.stderr)
                continue

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
            if talk_page.exists() and not talk_page.has_permission('edit'):
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

            def save(store):
                store.set_failure(type, list(failed_only))
                store.set_state(type, list(notified_files), 'notified')
            with_store(save)
            raise

        notified_files.update(states)

    with_store(lambda store: store.set_state(type, list(file_states.values()), 'notified'))


process_list('discussion', DiscussionFormatter)
process_list('speedy', SpeedyFormatter)
process_list('nopermission', NoPermissionFormatter)
with_store(lambda store: store.expire_failed())
