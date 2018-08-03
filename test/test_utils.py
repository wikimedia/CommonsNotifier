import unittest
from datetime import datetime
from commonsbot.utils import get_nomination_page, check_already_posted, PerWikiMapper
from pywikibot import Site, Page


class TestParsing(unittest.TestCase):

    def test_empty(self):
        self.assertIsNone(get_nomination_page(''))

    def test_garbage(self):
        cases = [
            ' ',
            ' \t',
            'foobar',
            '<nowiki></nowiki>',
            '{{some_other_template|subpage=foo}}',
            '{{Delete}}',
            'foo {{delete|reason=because}}',
            '{{delete|subpage}}',
            '{{delete|subpage=}}',
            '{{delete|subpage= }}',
            # '{{delete|subpage=_}}'
        ]

        for case in cases:
            with self.subTest():
                self.assertIsNone(get_nomination_page(case))

    def test_parsing(self):
        cases = [
            ('{{delete|subpage=foo}}', 'foo'),
            ('{{Delete|subpage=bar}}', 'bar'),
            ('{{delete}}foo{{delete|subpage=foo}}{{delete}}', 'foo'),
        ]
        for input, expected in cases:
            with self.subTest():
                self.assertEqual(expected, get_nomination_page(input))

    def test_already_posted(self):
        cases = [
            # ('', False, 'empty string'),
            # ('foo', False, 'random string'),
            # ('<!-- COMMONSBOT: -->', False, 'incomplete tag'),
            # ('<!-- COMMONSBOT: speedy | 2017-05-15T13:30:00+00:00 | File.jpg -->', False, 'wrong discussion type'),
            # ('<!-- COMMONSBOT: discussion | 2017-05-15T13:30:00+00:00 | Fail.jpg -->', False, 'wrong filename'),
            # ('<!-- COMMONSBOT: discussion | 2017-05-15T99:99:00+00:00 | File.jpg -->', True, 'invalid date'),
            # ('<!-- COMMONSBOT: discussion | 2018-05-15T13:30:00+00:00 | File.jpg -->', True, 'has recent post'),
            ('<!-- COMMONSBOT: discussion | 2017-05-15T13:30:00+00:00 | File.jpg -->', False, 'has old posts'),
            # ('<!-- COMMONSBOT: discussion | 2018-05-15T13:30:00+00:00 | File.jpg --><!-- COMMONSBOT: discussion | 2017-05-15T13:30:00+00:00 | File.jpg -->', True, 'match after a miss'),
        ]

        now = datetime(2018, 6, 1)
        for input, expected, msg in cases:
            with self.subTest():
                result = check_already_posted(input, 'File.jpg', 'discussion', now=now)
                self.assertEqual(expected, result, msg)


class TestMapper(unittest.TestCase):

    def test_all(self):
        site1 = Site('en')
        site2 = Site('de')
        pn = ['page1', 'page2', 'page3']
        sites = [site1, site2]
        pages = [Page(s, '%s-%s' % (p, s.dbName())) for p in pn for s in sites]

        m = PerWikiMapper(2)
        m.add('Foo.jpg', pages[0])
        for index in [1, 2, 3]:
            m.add('Bar.jpg', pages[index])
        m.add('Baz.jpg', pages[1])
        m.add('Quux.jpg', pages[1])

        file_list = []
        for page, files in m.files_per_page():
            file_list.append(page.title() + '>' + '|'.join(files))

        expected = [
            'Page1-enwiki>Foo.jpg',
            'Page2-enwiki>Bar.jpg',
            'Page1-dewiki>Bar.jpg|Baz.jpg|Quux.jpg',
            'Page2-dewiki>Bar.jpg'
        ]
        self.assertEqual(sorted(file_list), sorted(expected))


if __name__ == '__main__':
    unittest.main()
