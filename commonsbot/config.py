import json

file = open('config.json', 'rt')
settings = json.loads(file.read())
file.close()

file = open('wikis-enabled', 'r')
settings['wikis'] = [s.strip() for s in file.readlines()]
file.close()
