#!/usr/bin/python3

from commonsbot import mysql, lists
from commonsbot.state import DeletionStateStore, DeletionState
from pywikibot.site import Namespace
import pprint

commons = mysql.connect('replica')
userdb = mysql.connect('userdb')

maker = lists.RecursiveCategoryScanner(commons)
slow_deletions = maker.scan( 'Deletion_requests', depth=2)
print('----------')
# for row in slow_deletions: pprint.pprint(row)
print('%s pages found' % len(slow_deletions))

store = DeletionStateStore(userdb)
file = DeletionState('Foo.jpg', 'discussion', 'new')
store.load_state([], 'ddadasads')
store.save_state([file])
# files = store.refresh_state(slow_deletions, 'discussion')
