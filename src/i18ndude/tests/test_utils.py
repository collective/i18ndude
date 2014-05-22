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

    def test_wrapString_wrapping_first_line_edge_case(self):
        """Lines that are just a bit shorter than MAX_WIDTH are still longer
        at the end, as the line also contains the 'msgstr '.
        This test makes sure that this edge case is taken care of
        """
        msgstr_length = len('msgstr ')
        # the maximum amount of characters on the first line should be:
        max_line_length = i18ndude.utils.MAX_WIDTH - msgstr_length - 2

        line = 'a' * max_line_length
        self.assertEqual(wrapString(line), [line])

        # but only one character more would make it split into two lines
        line += 'a'
        self.assertEqual(wrapString(line), ['', line])

    def test_wrapString_wrapping_multiline(self):
        # This does not fit on a single line.
        line = 'a'*20 + ' ' + 'b'*50 + ' ' + 'c'*20+ ' ' + 'd'*50
        self.assertEqual(wrapString(line),
                         ['',
                          'a'*20 + ' ' + 'b'*50 + ' ',
                          'c'*20 + ' ' + 'd'*50])

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

        # Accept a line of 12: 3 characters plus 2 quotes (and 'msgstr ').
        i18ndude.utils.MAX_WIDTH = 12
        self.assertEqual(wrapString('aaa'), ['aaa'])
        self.assertEqual(wrapString('aaaa'), ['', 'aaaa'])
        self.assertEqual(wrapString('aaa' + ' ' + 'a'*12),
                         ['', 'aaa ', 'a'*12])

        # If this is 2 or less, we do not wrap lines.
        i18ndude.utils.MAX_WIDTH = 2
        self.assertEqual(wrapString('aaa aaaaa'), ['aaa aaaaa'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUtils))
    return suite
