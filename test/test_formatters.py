import unittest
from commonsbot.formatters import Formatter, DiscussionFormatter, SpeedyFormatter
from commonsbot.i18n import I18n
from commonsbot.state import DeletionState
from pywikibot import Site, FilePage

class TestFormatters(unittest.TestCase):
    def test_format_throws(self):
        i18n = I18n.factory('en')
        f = Formatter('speedy', i18n)
        with self.assertRaises(ValueError):
            f.format([])


    def test_discussion_formatter(self):
        self.maxDiff = None
        i18n = I18n.factory('en')
        f = DiscussionFormatter(i18n)
        states = self.get_test_data('discussion')

        expected = """

== {{PLURAL:2|A Commons file|Commons files}} used on this page {{PLURAL:2|has|have}} been nominated for deletion ==
The following Wikimedia Commons {{PLURAL:2|file|files}} used on this page {{PLURAL:2|has|have}} been nominated for deletion:
* [[commons:File:File1.jpg|File1.jpg]] ([[commons:Commons:Deletion requests/File1.jpg|discussion]])
* [[commons:File:File2.jpg|File2.jpg]] ([[commons:Commons:Deletion requests/File2.jpg|discussion]])
Participate in the deletion {{PLURAL:2|discussions}} at the nomination {{PLURAL:2|pages}} linked above. ~~~~
"""
        result = f.format(states)
        self.assertEqual(expected, result)

        states[1].discussion_page = states[0].discussion_page
        expected = """

== {{PLURAL:2|A Commons file|Commons files}} used on this page {{PLURAL:2|has|have}} been nominated for deletion ==
The following Wikimedia Commons {{PLURAL:2|file|files}} used on this page {{PLURAL:2|has|have}} been nominated for deletion:
* [[commons:File:File1.jpg|File1.jpg]]
* [[commons:File:File2.jpg|File2.jpg]]
Participate in the deletion discussion at the [[commons:Commons:Deletion requests/File1.jpg|nomination page]]. ~~~~
"""
        result = f.format(states)
        self.assertEqual(expected, result)

        expected = """

== {{PLURAL:1|A Commons file|Commons files}} used on this page {{PLURAL:1|has|have}} been nominated for deletion ==
The following Wikimedia Commons {{PLURAL:1|file|files}} used on this page {{PLURAL:1|has|have}} been nominated for deletion:
* [[commons:File:File1.jpg|File1.jpg]]
Participate in the deletion discussion at the [[commons:Commons:Deletion requests/File1.jpg|nomination page]]. ~~~~
"""
        result = f.format(states[:1])
        self.assertEqual(expected, result)


    def test_speedy_formatter(self):
        self.maxDiff = None
        i18n = I18n.factory('en')
        f = SpeedyFormatter(i18n)
        states = self.get_test_data('speedy')

        expected = """

== {{PLURAL:2|A Commons file|Commons files}} used on this page {{PLURAL:2|has|have}} been nominated for speedy deletion ==
The following Wikimedia Commons {{PLURAL:2|file|files}} used on this page {{PLURAL:2|has|have}} been nominated for speedy deletion:
* [[File:File1.jpg|File1.jpg]]
* [[File:File2.jpg|File2.jpg]]
You can see the {{PLURAL:2|reason|reasons}} for deletion at the file description {{PLURAL:2|page|pages}} linked above. ~~~~
"""
        result = f.format(states)
        self.assertEqual(expected, result)

    def get_test_data(self, type):
        state1 = DeletionState('File1.jpg', type, 'new')
        state1.discussion_page = 'Commons:Deletion requests/File1.jpg'
        state2 = DeletionState('File2.jpg', type, 'new')
        state2.discussion_page = 'Commons:Deletion requests/File2.jpg'
        return [state1, state2]