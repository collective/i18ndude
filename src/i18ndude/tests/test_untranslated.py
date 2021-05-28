"""Tests for finding untranslated prose.
"""
import os
import sys
import unittest
import xml.sax
import io
import i18ndude.untranslated
from argparse import Namespace
from i18ndude.script import find_untranslated as script
from i18ndude.tests.utils import suppress_stdout, TESTDATA_DIR

PY3 = sys.version_info > (3,)
if PY3:
    unicode = str
    unicode_StringIO = io.StringIO
else:
    import StringIO
    # io.StringIO in python2 (but not in python3) raises:
    # TypeError: unicode argument expected, got 'str'
    unicode_StringIO = StringIO.StringIO


def find_untranslated(input):
    out = unicode_StringIO()
    parser = xml.sax.make_parser(['expat'])
    handler = i18ndude.untranslated.VerboseHandler(parser, out)
    parser.setContentHandler(handler)
    parser.parse(unicode_StringIO(input))
    return out.getvalue()


class TestUntranslated(unittest.TestCase):

    def test_untranslated_content(self):
        """
        find-untranslated can find strings missing the i18n:translate marker
        and it will show an error.
        """
        result_with_errors = find_untranslated('<div><p>foo</p></div>')
        self.assertIn(
            'i18n:translate missing for this:\n"""\nfoo\n"""',
            result_with_errors)
        self.assertIn(
            '(0 warnings, 1 errors)',
            result_with_errors)

    def test_untranslated(self):
        """
        find-untranslated finds no error if the i18n:translate marker is set.
        """
        result_without_errors = find_untranslated(
            '<div><p i18n:translate="">foo</p></div>')
        self.assertNotIn(
            'i18n:translate missing',
            result_without_errors)
        self.assertIn('(0 warnings, 0 errors)', result_without_errors)

    def test_ignore_untranslated_with_marker(self):
        """
        Adding the i18n:ignore marker will skip untranslated strings.
        """
        result_with_marker = find_untranslated(
            '<div><p i18n:ignore="">foo</p></div>')
        self.assertIn('(0 warnings, 0 errors)', result_with_marker)

    def test_ignore_untranslated_attribute(self):
        """
        Attributes missing the i18n:attributes marker will cause
        find-untranslated to show an error.

        Attributes marked with i18n:ignore-attributes will cause
        find-untranslated to not show an error.
        """
        result_without_attributes = find_untranslated(
            '<div><a title="bar" i18n:translate="">spam</a></div>')
        self.assertIn(
            'title attribute of <a> lacks i18n:attributes',
            result_without_attributes)
        self.assertIn('(0 warnings, 1 errors)', result_without_attributes)

        result_with_ignore_attributes = find_untranslated(
            '''<div><a title="bar"
                i18n:ignore-attributes="title"
                i18n:translate=""
                >spam</a></div>''')
        self.assertIn('(0 warnings, 0 errors)', result_with_ignore_attributes)

    def test_ignore_untranslated_attribute_complain_about_other_attrs(self):
        """
        find-untranslated will find an error if not all attributes are marked
        to be ignored.
        """
        result_without_attributes = find_untranslated(
            '''<div><img title="bar" alt="qux"
            i18n:ignore-attributes="title"/></div>''')
        self.assertIn(
            'alt attribute of <img> lacks i18n:attributes',
            result_without_attributes)
        self.assertIn('(0 warnings, 1 errors)', result_without_attributes)

    def test_ignore_untranslated_attribute_multiple_attrs(self):
        """
        find-untranslated finds no error if multiple attributes are marked
        to be ignored.
        """
        result_with_multiple_ignore_attributes = find_untranslated(
            '''<div><img title="bar" alt="qux"
            i18n:ignore-attributes="title;alt"/></div>''')
        self.assertIn('(0 warnings, 0 errors)',
                      result_with_multiple_ignore_attributes)

    def test_find_untranslated_placeholder_attribute(self):
        result_with_untranslated_placeholder = find_untranslated(
            '<div><input type="text" placeholder="search for bar"/></div>')
        self.assertIn(
            'placeholder attribute of <input> lacks i18n:attributes',
            result_with_untranslated_placeholder)

    def test_ignore_translated_placeholder_attribute(self):
        result_with_translated_placeholder = find_untranslated(
            '<div><input type="text" i18n:attributes="placeholder" placeholder="search for bar"/></div>')
        self.assertNotIn(
            'placeholder attribute of <input> lacks i18n:attributes',
            result_with_translated_placeholder)

    def test_find_untranslated_aria_label_attribute(self):
        result_with_untranslated_aria_label = find_untranslated(
            '<div><button aria-label="cookies"/></div>')
        self.assertIn(
            'aria-label attribute of <button> lacks i18n:attributes',
            result_with_untranslated_aria_label)

        result_with_translated_aria_label = find_untranslated(
            '<div><button aria-label="cookies" i18n:attributes="aria-label"/></div>')
        self.assertNotIn(
            'lacks i18n:attributes',
            result_with_translated_aria_label)

    def test_find_untranslated_disallows_nonword_chars_in_i18n_name(self):
        error = 'invalid non-word characters (space, punctuation) in i18n:name'
        result_with_space_in_name = find_untranslated(
            '<div i18n:translate="">Something <span i18n:name="xfoo xbar">amiss</span></div>')
        self.assertIn(error, result_with_space_in_name)
        self.assertIn('1 errors', result_with_space_in_name)
        result_with_slash_in_name = find_untranslated(
            '<div i18n:translate="">Something <span i18n:name="xfoo/xbar">amiss</span></div>')
        self.assertIn(error, result_with_slash_in_name)
        self.assertIn('1 errors', result_with_slash_in_name)
        result_with_dash_in_name = find_untranslated(
            '<div i18n:translate="">Something <span i18n:name="x_foo-x_bar">amiss</span></div>')
        self.assertNotIn(error, result_with_dash_in_name)
        self.assertIn('0 errors', result_with_dash_in_name)


class TestUntranslatedScript(unittest.TestCase):

    def test_script_template_1(self):
        path = os.path.join(TESTDATA_DIR, 'input', 'test1.pt')
        with suppress_stdout():
            result = script(Namespace(
                silent=False, nosummary=False, files=[path]))
        self.assertEqual(result, 0)

    def test_script_template_3(self):
        path = os.path.join(TESTDATA_DIR, 'input', 'test3.pt')
        with suppress_stdout():
            result = script(Namespace(
                silent=False, nosummary=False, files=[path]))
        self.assertEqual(result, 1)

    def test_script_template_4(self):
        path = os.path.join(TESTDATA_DIR, 'input', 'test4.pt')
        output = unicode_StringIO()
        old_stdout = sys.stdout
        sys.stdout = output
        try:
            result = script(Namespace(
                silent=False, nosummary=False, files=[path]))
        finally:
            sys.stdout = old_stdout
        self.assertEqual(result, 1)
        # A specific line should be reported as missing an i18n.
        self.assertIn('{}:16'.format(path), output.getvalue())

    def test_script_chameleon(self):
        path = os.path.join(TESTDATA_DIR, 'input', 'chameleon.pt')
        with suppress_stdout():
            result = script(Namespace(
                silent=False, nosummary=False, files=[path]))
        self.assertEqual(result, 0)

    def test_script_directory(self):
        path = os.path.join(TESTDATA_DIR, 'input')
        with suppress_stdout():
            result = script(Namespace(
                silent=False, nosummary=False, files=[path]))
        self.assertEqual(result, 2)
