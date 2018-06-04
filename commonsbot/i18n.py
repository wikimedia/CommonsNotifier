import json
from os import path
import re

def format(msg, params):
    """
    Expands parameters for a MediaWiki-style message string
    @param msg: format string
    @type msg: str
    @param params: message parameters
    @type params: tuple
    """

    if len(params) == 0:
        return msg

    used = set()
    last_index = 0
    result = ''
    for match in re.finditer('(?<=\\$)\\d+', msg):
        ms = match.group()
        index = int(ms) - 1
        if index >= len(params):
            raise ValueError('Message has parameter $%s but was passed only %d parameters' % (ms, len(params)))
        result += msg[last_index:match.start() - 1]
        result += str(params[index])
        last_index = match.end()
        used.add(index)

    result += msg[last_index:]

    param_set = set(range(len(params)))
    if param_set != used:
        raise ValueError('Mismatch between parameters passed and found in the message "%s"' % msg)
    return result


class I18n(object):
    """
    Represents a set of localisation messages in a single language
    """
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
        if type(params) != tuple:
            params = (params,)
        return format(self.data[key], params)
