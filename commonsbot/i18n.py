import json
import sys
from os import path
import re
from glob import glob

_presence_cache = {}


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

    result += msg[last_index:]

    return result


def language_has_all_messages(code):
    """
    Verifies that a language has all the required messages
    @param code: language code to check
    @type code: str
    @rtype: bool
    """

    # We compare all the languages against English. If even it doesn't have a
    # certain message, I18n.msg() will throw
    if code == 'en':
        return True

    if code in _presence_cache:
        return _presence_cache[code]

    en = I18n.factory('en')
    lang = I18n.factory(code)
    messages = lang.keys()
    result = True
    for msg in en.keys():
        if msg[0] == 0:
            # Metadata
            continue
        if msg not in messages:
            print('Language "%s" misses message "%s"' % (code, msg), file=sys.stderr)
            result = False
    _presence_cache[code] = result
    return result


class MessageNotFound(Exception):
    """
    Exception thrown when a message is not found
    """

    def __init__(self, lang_code, message_key):
        super.__init__("Language %s misses message '%s'" % (lang_code, message_key))


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
        """
        Static factory
        @param language: Langage code
        @type language: str
        @rtype: I18n
        """
        if language in I18n._aliases:
            language = I18n._aliases[language]
        if language in I18n._cache:
            return I18n._cache[language]

        obj = I18n(language)
        I18n._cache[language] = obj
        return obj

    @staticmethod
    def _directory():
        dirname = path.dirname(__file__)
        return path.normpath('%s/../i18n' % dirname)

    def __init__(self, language):
        self.language = language
        filename = '%s/%s.json' % (I18n._directory(), self.language)
        file = open(filename, 'r', encoding='utf8')
        self.data = json.load(file)
        file.close()

    def msg(self, key, params=()):
        if key not in self.data:
            raise MessageNotFound(self.language, key)
        if type(params) != tuple:
            params = (params,)
        return format(self.data[key], params)

    def keys(self):
        """
        Returns message keys this language has
        @rtype: list
        """
        return self.data.keys()

    @staticmethod
    def languages():
        """
        Returns a list of language codes available, qqq is not included
        @rtype: list
        """
        list = []
        for file in glob(I18n._directory() + '/*.json'):
            lang = path.splitext(path.basename(file))[0]
            if lang != 'qqq':
                list.append(lang)
        return sorted(list)
