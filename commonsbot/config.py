import json
import os

file = open('config.json', 'rt')
settings = json.loads(file.read())
file.close()
db_connections = settings['db_connections']

dry_run = False
if 'dry-run' in settings:
    dry_run = settings['dry-run']

file = open('wikis-enabled', 'r')
wikis = set([s.strip() for s in file.readlines()])
file.close()

mysql_config_file = None
for dir in ['.', os.environ['HOME']]:
    for file in ['my.cnf','replica.my.cnf']:
        file = '%s/%s' % (dir, file)
        if os.path.isfile(file):
            mysql_config_file = file
            break
if mysql_config_file is None:
    raise OSError('replica.my.cnf not found!')

__all__ = ('settings', 'db_connections', 'mysql_config_file')
