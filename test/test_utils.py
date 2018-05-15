import unittest
from commonsbot.utils import get_nomination_page


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


if __name__ == '__main__':
    unittest.main()
