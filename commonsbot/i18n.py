import json
from os import path
import re

def format(msg, params):
    if len(params) == 0:
        return msg

    used = set()
    for match in re.finditer('(?<=\\$)\\d+', msg):
        ms = match.group()
        index = int(ms) - 1
        if index >= len(params):
            raise ValueError('Message has parameter $%s but was passed only %d parameters' % (ms, len(params)))
        msg = msg.replace('$' + ms, str(params[index]), 1)
        used.add(index)

    param_set = set(range(len(params)))
    if param_set != used:
        raise ValueError('Mismatch between parameters passed and found in the message')
    return msg

class I18n(object):
    _cache = {}
    _aliases = {
        'test': 'en'
    }

    @staticmethod
    def factory(language):
        if language in I18n._aliases:
            language = I18n._aliases[language]
        if language in I18n._cache:
            return I18n._cache[language]

        obj = I18n(language)
        I18n._cache[language] = obj
        return obj

    def __init__(self, language):
        self.language = language
        dir = path.dirname(__file__)
        filename = path.normpath('%s/../i18n/%s.json' % (dir, self.language))
        file = open(filename, 'r')
        self.data = json.loads(file.read())
        file.close()

    def msg(self, key, params=()):
        return format(self.data[key], params)
