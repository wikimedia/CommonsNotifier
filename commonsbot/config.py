import json

file = open('config.json')
settings = json.loads(file.read())
file.close()
