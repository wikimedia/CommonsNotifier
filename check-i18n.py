#!/usr/bin/python3
"""
Outputs localization statistics for every language present
"""

from commonsbot.i18n import I18n, language_has_all_messages

for lang in I18n.languages():
    if language_has_all_messages(lang):
        print("Language %s has all messages" % lang)
