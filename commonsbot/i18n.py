import json
import os


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
        dir = os.path.dirname(__file__)
        filename = os.path.normpath('%s/../i18n/%s.json' % (dir, self.language))
        file = open(filename, 'r')
        self.data = json.loads(file.read())
        file.close()
    
    def get(self, key):
        return self.data[key]
