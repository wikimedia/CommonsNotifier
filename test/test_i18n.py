import unittest
from commonsbot.i18n import format


class TestI18n(unittest.TestCase):

    def test_format(self):
        cases = [
            # format string, params, expected
            ('', (), ''),
            ('foo', (), 'foo'),
            ('$1', ('foo',), 'foo'),
            ('uh $1 bar $1 baz $1', ('foo',), 'uh foo bar foo baz foo'),
            ('$2$1', ('foo', 'bar'), 'barfoo'),
            ('$1 $2', ('$2 bill', "y'all"), "$2 bill y'all"),
            ('$1 bill', (), '$1 bill'),
            ('not using a parameter', ('whatever'), 'not using a parameter'),
        ]

        for msg, params, expected in cases:
            with self.subTest():
                result = format(msg, params)
                self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
