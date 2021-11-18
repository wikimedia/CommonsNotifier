#!/usr/bin/python3

from commonsbot import mysql
from commonsbot.state import DeletionStateStore, DeletionState
from pywikibot import Site, Category
from pywikibot.pagegenerators import CategorizedPageGenerator
from pywikibot.site import Namespace
from pprint import pprint

commons = Site('commons', 'commons')
userdb = mysql.connect()
store = DeletionStateStore(userdb)


def load_files(categories, depth):
    """
    Returns a list of unique files in categories

    @param categories: List of Commons category names as strings
    @type categories: list
    @param depth: Category recursion depth
    @type depth: int
    @rtype: list
    """
    files = set()
    for cat in categories:
        cat = Category(commons, cat)
        generator = CategorizedPageGenerator(cat,
                                             recurse=depth,
                                             namespaces=Namespace.FILE)
        for page in generator:
            files.add(page.title(with_ns=False))

    return list(files)


def make_list(type, categories, depth, delay):
    """
    Makes a list of files up for deletion

    @param type: Deletion type
    @type type: str
    @param categories: List of Commons category names as strings
    @type categories: list
    @param depth: Category recursion depth
    @type depth: int
    @param delay: For how long should a file be up for deletion to be reported, in seconds
    @type delay: int
    """
    files = load_files(categories, depth)
    print('%s pages found for %s deletion' % (len(files), type))

    states = store.refresh_state(files, type)
    file = open('lists/%s.txt' % type, 'w', encoding='utf8')
    count = 0
    for state in states:
        if state.state == 'new' and state.age() >= delay:
            file.write("%s\n" % state.file_name)
            count += 1
    file.close()
    print('%d files sent for tagging' % count)


make_list('discussion', ['Deletion_requests'], depth=2, delay=60 * 60)
make_list('speedy',
          [
              'Candidates for speedy deletion',
              'Copyright violations',
          ], depth=False, delay=60 * 15)
make_list('nopermission', ['Media missing permission'], depth=1, delay=60 * 60)
