# -*- coding: utf-8 -*-
# ****************************************
# * Pywikibot settings file for this bot *
# ****************************************

# Required by Pywikibot, but not needed for anything we use
mylang = 'en'
family = 'wikipedia'

# Username across the cluster
usernames['wikipedia']['*'] = \
    usernames['wikibooks']['*'] = \
    usernames['wikinews']['*'] = \
    usernames['wikiquote']['*'] = \
    usernames['wikisource']['*'] = \
    usernames['wikiversity']['*'] = \
    usernames['test']['*'] = \
    'MaxSem test bot'

# Secret password file, see
# https://www.mediawiki.org/wiki/Manual:Pywikibot/BotPasswords
# for instructions
password_file = 'user-password.py'

# Setting this to True generates lots of debug output
verbose_output = False
