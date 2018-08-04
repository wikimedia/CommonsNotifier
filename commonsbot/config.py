import json
import os

basedir = os.path.dirname(os.path.dirname(__file__)) + '/'

file = open(basedir + 'config.json', 'rt')
settings = json.loads(file.read())
file.close()

dry_run = settings['dry-run']

file = open(basedir + 'wikis-enabled', 'r')
wikis = set([s.strip() for s in file.readlines()])
file.close()

mysql_config_file = None
for dir in ['.', basedir, os.environ['HOME']]:
    for file in ['my.cnf', 'replica.my.cnf']:
        file = '%s/%s' % (dir, file)
        if os.path.isfile(file):
            mysql_config_file = file
            break


def for_wiki(dbname):
    wikis = settings['wiki-options']
    result = wikis['default'].copy()
    if dbname in wikis:
        result.update(wikis[dbname])

    return result


__all__ = ('settings', 'mysql_config_file', 'dry_run', 'for_wiki')
