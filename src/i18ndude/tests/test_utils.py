# -*- coding: utf-8 -*-
import unittest

from i18ndude.utils import wrapString, MAX_WIDTH


class TestUtils(unittest.TestCase):

    def test_wrapString(self):
        # We can change the WRAP and MAX_WIDTH settings by using
        # command line options.  We save the original here.
        import i18ndude.utils
        orig_max_width = i18ndude.utils.MAX_WIDTH
        orig_wrap = i18ndude.utils.WRAP

        # By default we do not wrap.
        line = 'a'*50 + ' ' + 'b'*50
        self.assertEqual(wrapString(line),
                         ['a'*50 + ' ' + 'b'*50])

        # That is not very interesting, so we enable wrapping for the
        # rest of the test.
        i18ndude.utils.WRAP = True

        # This all fits on one line.
        self.assertEqual(wrapString(''), [''])
        self.assertEqual(wrapString('a'), ['a'])
        self.assertEqual(wrapString('a b'), ['a b'])

        # This no longer fits.
        line = 'a'*20 + ' ' + 'b'*50 + ' ' + 'c'*20+ ' ' + 'd'*50
        self.assertEqual(wrapString(line),
                         ['',
                          'a'*20 + ' ' + 'b'*50 + ' ',
                          'c'*20+ ' ' + 'd'*50])

        # Look for the maximum that can fit on a single line.  This is
        # the maximum width, minus a starting and ending quote.
        max_one_line = MAX_WIDTH - 2
        line = 'a'*40 + ' ' + 'b'*36
        self.assertEqual(len(line), max_one_line)
        self.assertEqual(wrapString(line), [line])

        # With one extra character we must split.
        line += 'b'
        self.assertEqual(wrapString(line),
                         ['',
                          'a'*40 + ' ',
                          'b'*37])

        # So, what happens when some words are really too long?
        A = 'a'*99
        B = 'b'*99
        C = 'c'*99
        self.assertEqual(wrapString(A), ['', A])
        line = ' '.join((A, B))
        self.assertEqual(wrapString(line), ['', A + ' ', B])
        line = ' '.join((A, B, C))
        self.assertEqual(wrapString(line), ['', A + ' ', B + ' ', C])

        # Accept a line of 5: 3 characters plus 2 quotes.
        i18ndude.utils.MAX_WIDTH = 5
        self.assertEqual(wrapString('aaa'), ['aaa'])
        self.assertEqual(wrapString('aaaa'), ['', 'aaaa'])
        self.assertEqual(wrapString('aaa aaaaa'), ['', 'aaa ', 'aaaaa'])

        # If this is 2 or less, we do not wrap lines.
        i18ndude.utils.MAX_WIDTH = 2
        self.assertEqual(wrapString('aaa aaaaa'), ['aaa aaaaa'])

        # Restory the original settings.
        i18ndude.utils.MAX_WIDTH = orig_max_width
        i18ndude.utils.WRAP = orig_wrap


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUtils))
    return suite
