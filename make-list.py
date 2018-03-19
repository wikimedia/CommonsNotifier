#!/usr/bin/python3

from commonsbot import mysql, lists
from commonsbot.state import DeletionStateStore, DeletionState
from pywikibot.site import Namespace
import pprint

commons = mysql.connect('replica')
userdb = mysql.connect('userdb')
maker = lists.RecursiveCategoryScanner(commons)
store = DeletionStateStore(userdb)


def make_list(type, categories, depth, delay):
    list = []
    for cat in categories:
        list.extend(maker.scan(cat, depth, (Namespace.FILE,)))
    print('%s pages found for %s deletion' % (len(list), type))
    states = store.refresh_state(list, type)
    file = open('lists/%s.txt' % type, 'w')
    count = 0
    for state in states:
        if state.state == 'new' and state.age() >= delay:
            file.write("%s\n" % state.file_name)
            count += 1
    file.close()
    print('%d files sent for tagging' % count)


make_list('discussion', ['Deletion_requests'], 2, delay=60 * 60)
make_list('speedy', ['Candidates_for_speedy_deletion'], 2, delay=60 * 15)
