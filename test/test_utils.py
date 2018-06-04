import unittest
from commonsbot.utils import get_nomination_page, PerWikiMapper
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
        self.assertEqual(file_list, expected)


if __name__ == '__main__':
    unittest.main()
