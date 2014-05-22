# -*- coding: utf-8 -*-
from i18ndude.utils import wrapString

import i18ndude.utils
import unittest


class TestUtils(unittest.TestCase):

    def setUp(self):
        self.original_max_width = i18ndude.utils.MAX_WIDTH
        self.original_wrap = i18ndude.utils.WRAP

        # Enable wrapping.
        i18ndude.utils.WRAP = True

    def tearDown(self):
        i18ndude.utils.MAX_WIDTH = self.original_max_width
        i18ndude.utils.WRAP = self.original_wrap

    def test_wrapString_no_wrapping(self):
        # Disable wrapping.
        i18ndude.utils.WRAP = False

        line = 'a'*50 + ' ' + 'b'*50
        self.assertEqual(wrapString(line),
                         ['a'*50 + ' ' + 'b'*50])

    def test_wrapString_wrapping_single_line(self):
        # Enable wrapping.
        i18ndude.utils.WRAP = True

        # This all fits on one line.
        self.assertEqual(wrapString(''), [''])
        self.assertEqual(wrapString('a'), ['a'])
        self.assertEqual(wrapString('a b'), ['a b'])

    def test_wrapString_wrapping_multiline(self):
        # This does not fit on a single line.
        line = 'a'*20 + ' ' + 'b'*50 + ' ' + 'c'*20+ ' ' + 'd'*50
        self.assertEqual(wrapString(line),
                         ['',
                          'a'*20 + ' ' + 'b'*50 + ' ',
                          'c'*20 + ' ' + 'd'*50])

        # Look for the maximum that can fit on a single line.  This is
        # the maximum width, minus a starting and ending quote.
        max_one_line = i18ndude.utils.MAX_WIDTH - 2
        line = 'a'*40 + ' ' + 'b'*36
        self.assertEqual(len(line), max_one_line)
        self.assertEqual(wrapString(line), [line])

        # With one extra character we must split.
        line += 'b'
        self.assertEqual(wrapString(line),
                         ['',
                          'a'*40 + ' ',
                          'b'*37])

    def test_wrapString_wrapping_long_words(self):
        # What happens when some words are really too long?
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


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUtils))
    return suite
