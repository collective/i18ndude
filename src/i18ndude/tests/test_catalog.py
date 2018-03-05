# -*- coding: utf-8 -*-
from i18ndude import catalog
from i18ndude import utils
from .utils import PACKAGE_HOME
import os
import sys
import tempfile
import unittest
import warnings

PY3 = sys.version_info > (3,)
if PY3:
    unicode = str


class TestGlobal(unittest.TestCase):

    def test_isLiteralId(self):
        i = catalog.is_literal_id
        errortext = 'False literal msgid recognition'
        self.assertFalse(i('label_yes'), errortext)
        self.assertFalse(i('_'), errortext)
        self.assertTrue(i(' '), errortext)
        self.assertTrue(i(' _'), errortext)
        self.assertTrue(i('text'), errortext)
        self.assertTrue(i('This is a text.'), errortext)

    def test_originalComment(self):
        self.assertEqual(
            catalog.ORIGINAL_COMMENT,
            'Original: ',
            'Wrong original comment constant'
        )

    def test_defaultComment(self):
        self.assertEqual(
            catalog.DEFAULT_COMMENT,
            'Default: ',
            'Wrong default comment constant'
        )


class TestMessageEntry(unittest.TestCase):

    def setUp(self):
        self.me = catalog.MessageEntry
        self.msgid = 'test msgid'
        self.msgstr = 'test text'
        self.references = ['test1.pt', 'test2.pt']
        self.default_text = 'test default'
        self.default_comment = '%s"%s"' % (catalog.DEFAULT_COMMENT, self.default_text)  # noqa
        self.automatic_comments = ['first line', 'second line', self.default_comment]  # noqa
        self.orig_text = 'test original'
        self.orig_comment = '%s"%s"' % (catalog.ORIGINAL_COMMENT, self.orig_text)  # noqa
        self.comments = ['A comment', self.orig_comment]

    def test_init(self):
        me = self.me
        me1 = me(self.msgid)
        self.assertEqual(me1.msgid, self.msgid, 'msgid not set correctly')
        me1 = me(self.msgid, msgstr=self.msgstr)
        self.assertEqual(me1.msgid, self.msgid, 'msgid not set correctly')
        self.assertEqual(me1.msgstr, self.msgstr, 'msgstr not set correctly')

        me1 = me(self.msgid, msgstr=self.msgstr, references=self.references)
        self.assertEqual(me1.msgid, self.msgid, 'msgid not set correctly')
        self.assertEqual(me1.msgstr, self.msgstr, 'msgstr not set correctly')
        self.assertEqual(me1.references, self.references, 'references not set correctly')  # noqa

        me1 = me(self.msgid, msgstr=self.msgstr, comments=self.comments)
        self.assertEqual(me1.msgid, self.msgid, 'msgid not set correctly')
        self.assertEqual(me1.msgstr, self.msgstr, 'msgstr not set correctly')
        self.assertEqual(me1.comments, self.comments, 'comments not set correctly')  # noqa
        self.assertEqual(me1.getOriginalComment(), self.orig_comment, 'Original comment not set correctly')  # noqa
        self.assertEqual(me1.getOriginal(), self.orig_text, 'Original text not set correctly')  # noqa

        me2 = me(self.msgid, msgstr=self.msgstr, automatic_comments=self.automatic_comments)  # noqa
        self.assertEqual(me2.msgid, self.msgid, 'msgid not set correctly')
        self.assertEqual(me2.msgstr, self.msgstr, 'msgstr not set correctly')
        self.assertEqual(me2.automatic_comments, self.automatic_comments, 'comments not set correctly')  # noqa
        self.assertEqual(me2.getDefaultComment(), self.default_comment, 'Default comment not set correctly')  # noqa
        self.assertEqual(me2.getDefault(), self.default_text, 'Default text not set correctly')  # noqa


class TestMessageCatalogInit(unittest.TestCase):

    def setUp(self):
        self.mc = catalog.MessageCatalog
        self.me = catalog.MessageEntry
        self.file = os.path.join(PACKAGE_HOME, 'input', 'test-en.po')
        self.emptyfile = os.path.join(PACKAGE_HOME, 'input', 'empty-en.po')

        self.commentary_header = [
            'Translation of test.pot to English',
            'Hanno Schlichting <schlichting@bakb.net>, 2005']

        self.mimeheader = {
            'Language-Code': 'en',
            'Domain': 'testing',
            'PO-Revision-Date': '2005-08-10 21:15+0000',
            'Content-Transfer-Encoding': '8bit',
            'Language-Name': 'English',
            'Plural-Forms': 'nplurals=1; plural=0;',
            'Project-Id-Version': 'i18ndude',
            'Preferred-Encodings': 'utf-8 latin1',
            'Last-Translator': u'Unicödé Guy',
            'Language-Team': 'Plone i18n <plone-i18n@lists.sourceforge.net>',
            'POT-Creation-Date': '2005-08-01 12:00+0000',
            'Content-Type': 'text/plain; charset=utf-8', 'MIME-Version': '1.0'
        }

        self.msgids = {
            u'msgid1': self.me(
                'msgid1',
                msgstr='msgstr1',
                references=['file1', 'file2'],
                automatic_comments=['Default: "msgstr1"'],
                comments=['comment1']),

            u'msgid2': self.me(
                'msgid2',
                msgstr='msgstr2',
                references=['file2']),

            u'msgid3': self.me(
                'msgid3',
                msgstr='\\n\\nmsgstr\\n3',
                references=['file3'],
                comments=['comment3']),

            u'msgid4': self.me(
                'msgid4',
                msgstr='msgstr4',
                references=['file4']),

            u'msgid5': self.me(
                'msgid5',
                msgstr='msgstr5',
                comments=['comment5']),

            u'msgid6': self.me(
                'msgid6',
                msgstr='msgstr6'),

            u'msgid7': self.me(
                'msgid7',
                msgstr='msgstr7',
                comments=[', fuzzy']),

            u'msgid8': self.me(
                'msgid8'),

            u'msgid has spaces': self.me(
                'msgid has spaces',
                msgstr='msgstr has spaces',
                comments=['# I am a dead comment']),

            u'msgid_has_underlines': self.me(
                'msgid_has_underlines',
                msgstr='msgstr_has_underlines'),

            u'msgid_has_underlines and spaces': self.me(
                'msgid_has_underlines and spaces',
                msgstr='msgstr_has_underlines and spaces'),

            u'msgid for unicode text': self.me(
                'msgid for unicode text',
                msgstr=u'unicode msgstr \xb7\xb7\xb7'),

            u'msgid for unicode text with comment': self.me(
                'msgid for unicode text with comment',
                msgstr=u'unicode msgstr \xb7\xb7\xb7',
                references=['./folder/file_unicode'],
                automatic_comments=['Default: [···]']),

            u'msgid for text with german umlaut': self.me(
                'msgid for text with german umlaut',
                msgstr=u'\xe4\xf6\xfc\xdf text'),

            u'msgid for text with html-entity': self.me(
                'msgid for text with html-entity',
                msgstr='&quot;this&nbsp;is&laquo;&auml;&amp;&ouml;&raquo;&quot;'),  # noqa

            (u"Its quite annoying that all translation editors wrap "
             "translations strings at 80 characters, but then when you "
             "update the po files with i18ndude they are unwrapped and "
             "kept as huge lines. Can we fix that?"): self.me(
                 u"Its quite annoying that all translation editors wrap "
                 "translations strings at 80 characters, but then when you "
                 "update the po files with i18ndude they are unwrapped and "
                 "kept as huge lines. Can we fix that?",
                 msgstr=("Of course we can fix that. After all: i18ndude is "
                         "awesome, as I am sure you all agree."),
                 comments=[
                     ("https://github.com/collective/i18ndude/issues/3 "
                      "complains about long lines. But long comment lines "
                      "should be left intact."),
                     ("Note that the unix msgattrib command can wrap or "
                      "unwrap long lines in po files.")]),

            u'msgid_with_long_lines_including_backslash_n.': self.me(
                'msgid_with_long_lines_including_backslash_n.',
                msgstr=("Falls aktiv wird der entsprechende \\nLinkcycle einen"
                        " Button haben, mit dem man durch ihn blaettern kann. "
                        "mit dem man durch ihn blaettern kann. mit dem man "
                        "durch ihn blaettern kann. mit dem man durch ihn "
                        "blaettern kann.")),  # XXX

        }

    def test_init(self):
        failing = False
        try:
            catalog.MessageCatalog()
        except AssertionError:
            failing = True
        self.assertTrue(
            failing, 'Init without parameters should not be allowed.')

    def test_initWithDomain(self):
        domain = 'testing'
        test = self.mc(domain=domain)
        mime = catalog.DEFAULT_PO_MIME
        for key, value in mime:
            if key != 'Domain':
                self.assertEqual(
                    value,
                    test.mime_header[key],
                    'header mismatch on %s' % key
                )
            else:
                self.assertEqual(
                    domain,
                    test.mime_header['Domain'],
                    'Domain mismatch'
                )
        self.assertEqual(
            catalog.DEFAULT_PO_HEADER,
            test.commentary_header,
            'commentary header mismatch'
        )
        self.assertEqual(len(test), 0, 'Non-empty catalog')

    def test_initWithEmptyFile(self):
        test = self.mc(filename=self.emptyfile)
        mime = catalog.DEFAULT_PO_MIME
        for key, value in mime:
            self.assertEqual(
                value,
                test.mime_header[key],
                'header mismatch on %s' % key
            )

    def test_initWithEmptyFileAndDomain(self):
        failing = False
        try:
            self.mc(domain='testing', filename=self.emptyfile)
        except AssertionError:
            failing = True
        self.assertTrue(
            failing,
            'Init with filename and domain parameters is not allowed.'
        )

    def test_initWithFile(self):
        test = self.mc(filename=self.file)
        for key in test.mime_header:
            self.assertEqual(
                test.mime_header[key],
                self.mimeheader[key],
                'wrong mime header parsing:\nGot: %s !=\nExpected: %s'
                % (test.mime_header[key], self.mimeheader[key])
            )
        for value in test.commentary_header:
            self.assertTrue(
                value in self.commentary_header,
                'wrong commentary header parsing'
            )
        if not test == self.msgids:
            for key in test:
                self.assertTrue(
                    test[key] == self.msgids[key],
                    'error in po parsing:\nGot:      %s !=\nExpected: %s'
                    % (test[key], self.msgids[key])
                )


class TestMessageCatalog(unittest.TestCase):

    def setUp(self):
        self.domain = 'testing'
        self.mc = catalog.MessageCatalog(domain=self.domain)
        self.msgid = 'test msgid'
        self.msgstr = 'test text'
        self.references = ['test1.pt', 'test2.pt']
        self.default_text = 'test default'
        self.default_comment = '%s"%s"' % (catalog.DEFAULT_COMMENT, self.default_text)  # noqa
        self.automatic_comments = ['first line', 'second line', self.default_comment]  # noqa
        self.orig_text = 'test original'
        self.orig_comment = '%s"%s"' % (catalog.ORIGINAL_COMMENT, self.orig_text)  # noqa
        self.comments = ['A comment', self.orig_comment]

    def test_add(self):
        msgid = self.msgid
        msgstr = self.msgstr
        references = self.references
        automatic_comments = self.automatic_comments

        # add with msgid
        self.mc.add(msgid)
        self.assertTrue(msgid in self.mc, 'msgid not found in catalog')
        del self.mc[msgid]
        self.assertFalse(msgid in self.mc, 'msgid found in catalog')
        # add with msgid and msgstr
        self.mc.add(msgid, msgstr=msgstr)
        self.assertEqual(self.mc[msgid].msgstr, msgstr, 'msgstr not found in catalog.')  # noqa
        del self.mc[msgid]
        self.assertFalse(msgid in self.mc, 'msgid found in catalog')
        # add with msgid, msgstr and filename
        self.mc.add(msgid, msgstr=msgstr, references=references)
        self.assertEqual(self.mc[msgid].references, references, 'references not found in catalog.')  # noqa
        del self.mc[msgid]
        self.assertFalse(msgid in self.mc, 'msgid found in catalog')
        # add with msgid, msgstr, filename and excerpt
        self.mc.add(msgid, msgstr=msgstr, references=references, automatic_comments=automatic_comments)  # noqa
        self.assertEqual(self.mc[msgid].automatic_comments, automatic_comments, 'automatic_comments not found in catalog.')  # noqa
        del self.mc[msgid]
        self.assertFalse(msgid in self.mc, 'msgid found in catalog')

    def test_multipleAdd(self):
        msgid = self.msgid
        msgstr = self.msgstr
        references = self.references
        automatic_comments = self.automatic_comments

        self.mc.add(msgid, msgstr=msgstr, references=references, automatic_comments=automatic_comments)  # noqa
        self.mc.add(msgid, msgstr=msgstr, references=references, automatic_comments=automatic_comments)  # noqa
        self.assertTrue(len(self.mc) == 1, 'duplicate msgid')
        self.assertTrue(len(self.mc[msgid].references) == 2, 'references missing')  # noqa

    def test_originalComment(self):
        self.mc.add(self.msgid, msgstr=self.msgstr, references=self.references, automatic_comments=self.automatic_comments)  # noqa
        self.mc[self.msgid].comments.extend(self.comments)
        self.assertEqual(self.mc.getComments(self.msgid), self.comments, 'wrong comments')  # noqa
        self.assertEqual(self.mc.getOriginalComment(self.msgid), self.orig_comment, 'wrong original comment line')  # noqa
        self.assertEqual(self.mc.getOriginal(self.msgid), self.orig_text, 'wrong original comment text')  # noqa
        self.assertEqual(self.mc.getDefaultComment(self.msgid), self.default_comment, 'wrong default comment line')  # noqa
        self.assertEqual(self.mc.getDefault(self.msgid), self.default_text, 'wrong default comment text')  # noqa


class TestMessageCatalogSync(unittest.TestCase):

    def setUp(self):
        mc = catalog.MessageCatalog
        self.potfile = os.path.join(PACKAGE_HOME, 'input', 'synctest.pot')
        self.pofile = os.path.join(PACKAGE_HOME, 'input', 'synctest-de.po')
        self.pot = mc(filename=self.potfile)
        self.po = mc(filename=self.pofile)

    def test_sync(self):
        old_defaults = {}
        for id in self.po:
            old_defaults[id] = self.po[id].getDefault()
        self.po.sync(self.pot)
        self.assertTrue(len(self.pot) == len(self.po), 'number of messages does not match')  # noqa
        for msgid in self.pot:
            self.assertTrue(msgid in self.po, 'msgid %s could not be found' % self.pot[msgid])  # noqa
            self.assertTrue(self.po[msgid].references == self.pot[msgid].references)  # noqa
            defaults = self.po[msgid].getDefaults()
            if defaults is not None:
                for dc in defaults:
                    self.assertTrue(
                        dc == self.pot[msgid].getDefault() or
                        dc == old_defaults[msgid],
                        'Either old or new default comment is missing on msgid: %s' % msgid  # noqa
                    )


class TestMessagePoWriter(unittest.TestCase):

    def setUp(self):
        mc = catalog.MessageCatalog
        self.input = os.path.join(PACKAGE_HOME, 'input', 'test-en.po')
        self.output = os.path.join(PACKAGE_HOME, 'output', 'test-en.po')
        self.input2 = os.path.join(PACKAGE_HOME, 'input', 'test2-en.po')
        self.expectedOutput2 = os.path.join(PACKAGE_HOME, 'input', 'test2_expected-en.po')  # noqa
        self.output2 = os.path.join(PACKAGE_HOME, 'output', 'test2-en.po')
        self.catalog = mc(filename=self.input)
        self.catalog2 = mc(filename=self.input2)
        if os.path.exists(self.output):
            os.remove(self.output)
        if os.path.exists(self.output2):
            os.remove(self.output2)

    def test_write(self):
        # Explicitly enable wrapping here, as that is what we did in
        # the test po file.
        orig_wrap = utils.WRAP
        utils.WRAP = True
        fd = open(self.output, 'w')
        pow = catalog.POWriter(fd, self.catalog)
        pow.write(sort=True)
        fd.close()
        # Restore original value.
        utils.WRAP = orig_wrap

        input = open(self.input, 'r')
        output = open(self.output, 'r')

        # compare line by line
        inlines = input.readlines()
        outlines = enumerate(output.readlines())

        input.close()
        output.close()

        for i, result in outlines:
            orig = inlines[i]
            self.assertEqual(
                orig,
                result,
                'difference in line %s, \'%s\' != \'%s\''
                % (i, orig, result)
            )

    def test_writeSpecialComments(self):
        fd = open(self.output2, 'w')
        pow = catalog.POWriter(fd, self.catalog2)
        pow.write(sort=True)
        fd.close()

        output = open(self.output2, 'r')
        expected = open(self.expectedOutput2, 'r')

        # compare line by line
        outlines = output.readlines()
        explines = enumerate(expected.readlines())

        output.close()
        expected.close()

        for i, result in explines:
            orig = outlines[i]
            self.assertEqual(
                orig,
                result,
                'difference in line %s, Got: \'%s\' != Expected: \'%s\''
                % (i, orig, result)
            )

    def tearDown(self):
        if os.path.exists(self.output):
            os.remove(self.output)
        if os.path.exists(self.output2):
            os.remove(self.output2)


class TestMessagePTReader(unittest.TestCase):

    def setUp(self):
        self.me = catalog.MessageEntry
        self.input = os.path.join(PACKAGE_HOME, 'input')
        filename = self.input + os.sep + 'test1.pt'
        second_filename = self.input + os.sep + 'test3.pt'
        self.output = {
            u'Buzz': self.me(u'Buzz', references=[filename + ':21']),
            u'${foo} ${bar}': self.me(u'${foo} ${bar}', references=[filename + ':26']),  # noqa
            u'dig_this': self.me(u'dig_this', msgstr=u'Dig this', references=[filename + ':52']),  # noqa
            u'text_buzz': self.me(u'text_buzz', msgstr=u'Buzz', references=[filename + ':29', filename + ':31']),  # noqa
            u'some_alt': self.me(u'some_alt', msgstr=u'Some alt', references=[filename + ':15', second_filename + ':15']),  # noqa
            u'title_some_alt': self.me(u'title_some_alt', msgstr=u'Some title', references=[filename + ':15']),  # noqa
            u'Job started at ${datetime} by user ${userid}.': self.me(u'Job started at ${datetime} by user ${userid}.', references=[filename + ':46']),  # noqa
            u'spacing': self.me(u'spacing', msgstr=u'Space <br /> before and after.', references=[filename + ':37']),  # noqa
            u'spacing_strong': self.me(u'spacing_strong', msgstr=u'Please press your browser\'s <strong>Back</strong> button to try again.', references=[filename + ':41']),  # noqa
            u'<tt>domain</tt> is one of the <em>local domains</em>:': self.me(u'<tt>domain</tt> is one of the <em>local domains</em>:', references=[filename + ':49']),  # noqa
            u'odd': self.me(u'odd', references=[filename + ':58']),
            u'even': self.me(u'even', references=[filename + ':59']),
            u'Test for issue 15, html5 attributes without value': self.me(u'Test for issue 15, html5 attributes without value', references=[filename + ':62']),  # noqa
        }

    def test_read(self):
        ptr = catalog.PTReader(self.input, domain='testing')
        with warnings.catch_warnings(record=True) as log:
            warnings.simplefilter("always")
            # This call will give a warning from zope.tal.
            ptr.read()
            self.assertGreaterEqual(len(log), 1, log)
            contents = '\n'.join([str(x.message) for x in log])
            # Check that a few key elements are in the
            # warning, without wanting to check the exact
            # wording, as this can easily change.
            self.assertTrue("already exists with a different default"
                            in contents, 'missing "already exists"')
            self.assertTrue("bad: b'Buzzer', should be: b'Buzz'"  # py36
                            in contents or
                            "bad: Buzzer, should be: Buzz"  # py27
                            in contents,
                            u'bad Buzzer not in contents: {}'.format(contents))

        out = ptr.catalogs['testing']
        for key in out:
            self.assertTrue(
                key in self.output,
                'Failure in pt parsing.\nUnexpected msgid: %s' % key
            )
        for key in self.output:
            self.assertTrue(out[key] == self.output[key],
                            'Failure in pt parsing.\nGot:%s\nExpected:%s' %
                            (out[key], self.output[key]))
        self.assertEqual(len(out), len(self.output))


class TestMessagePYReader(unittest.TestCase):

    def setUp(self):
        self.me = catalog.MessageEntry
        dirpath = os.path.join(PACKAGE_HOME, 'input')
        filepath = os.path.join(dirpath, 'test2.py')
        self.input = dirpath
        self.output = {
            u'Zero': self.me(u'Zero', references=[filepath + ':4']),
            u'One': self.me(u'One', references=[filepath + ':5']),
            u'msgid_three': self.me(u'msgid_three', msgstr='Three', references=[filepath + ':10']),  # noqa
            u'msgid_four': self.me(u'msgid_four', msgstr='Four ${map}', references=[filepath + ':13']),  # noqa
            u'msgid_five': self.me(u'msgid_five', msgstr=u"五番目", references=[filepath + ':17']),  # noqa
            u'msgid_six': self.me(u'msgid_six', msgstr=u"\nLine 1\nLine 2\nLine 3\n", references=[filepath + ':19']),  # noqa
            # XXX This should not be found as it's in a different domain
            # instead it recognizes the domain as a msgstr now
            u'Out1': self.me(u'Out1', msgstr='running', references=[filepath + ':7'])  # noqa
        }

    def test_read_py(self):
        pyr = catalog.PYReader(self.input, 'testing')
        pyr.read()
        out = pyr.catalogs['testing']
        for key in out:
            self.assertTrue(
                key in self.output,
                'Failure in py parsing.\nUnexpected msgid: %s' % key)
        for key in self.output:
            self.assertTrue(
                out.get(key, False),
                'Failure in py parsing.\nMissing:%s' % self.output.get(key))
            self.assertTrue(
                out.get(key) == self.output.get(key),
                'Failure in py parsing.\nGot:%s\nExpected:%s' %
                (out.get(key), self.output.get(key))
            )
        self.assertEqual(len(out), len(self.output))


class TestMessageGSReader(unittest.TestCase):

    def setUp(self):
        self.me = catalog.MessageEntry
        dirpath = os.path.join(PACKAGE_HOME, 'input')
        filepath = os.path.join(dirpath, 'test.xml')
        self.input = dirpath
        self.output = {
            u'RSS feed':
                self.me(u'RSS feed',
                        references=[filepath]),
            u'Print this':
                self.me(u'Print this',
                        references=[filepath]),
        }

    def test_read(self):
        reader = catalog.GSReader(self.input, 'plone')
        reader.read()
        out = reader.catalogs['plone']
        for key in out:
            self.assertTrue(
                key in self.output,
                'Failure in gs parsing.\nUnexpected msgid: %s' % key)
        for key in self.output:
            self.assertTrue(
                out.get(key, False),
                'Failure in gs parsing.\nMissing:%s' % self.output.get(key))
            self.assertTrue(
                out.get(key) == self.output.get(key),
                'Failure in gs parsing.\nGot:%s\nExpected:%s' %
                (out.get(key), self.output.get(key))
            )
        self.assertEqual(len(out), len(self.output))


class TestMessageZCMLReader(unittest.TestCase):

    def setUp(self):
        self.me = catalog.MessageEntry
        dirpath = os.path.join(PACKAGE_HOME, 'input')
        filepath = os.path.join(dirpath, 'test.zcml')
        self.input = dirpath
        self.output = {
            u'Plone Site':
                self.me(u'Plone Site',
                        references=[filepath + ':14']),
            u'Profile for a default Plone.':
                self.me(u'Profile for a default Plone.',
                        references=[filepath + ':14']),
            u'Mandatory dependencies for a Plone site':
                self.me(u'Mandatory dependencies for a Plone site',
                        references=[filepath + ':22']),
            u'Adds title and description fields.':
                self.me(u'Adds title and description fields.',
                        references=[filepath + ':42']),
            u'Basic metadata':
                self.me(u'Basic metadata',
                        references=[filepath + ':42']),
            u'Content rule names should be translated.':
                self.me(u'Content rule names should be translated.',
                        references=[filepath + ':53']),
        }

    def test_read(self):
        reader = catalog.ZCMLReader(self.input, 'plone')
        reader.read()
        out = reader.catalogs['plone']
        for key in out:
            self.assertTrue(
                key in self.output,
                'Failure in zcml parsing.\nUnexpected msgid: %s' % key)
        for key in self.output:
            self.assertTrue(
                out.get(key, False),
                'Failure in zcml parsing.\nMissing:%s' % self.output.get(key))
            self.assertTrue(
                out.get(key) == self.output.get(key),
                'Failure in zcml parsing.\nGot:%s\nExpected:%s' %
                (out.get(key), self.output.get(key))
            )
        self.assertEqual(len(out), len(self.output))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestGlobal))
    suite.addTest(unittest.makeSuite(TestMessageEntry))
    suite.addTest(unittest.makeSuite(TestMessageCatalogInit))
    suite.addTest(unittest.makeSuite(TestMessageCatalog))
    suite.addTest(unittest.makeSuite(TestMessageCatalogSync))
    suite.addTest(unittest.makeSuite(TestMessagePoWriter))
    suite.addTest(unittest.makeSuite(TestMessagePTReader))
    suite.addTest(unittest.makeSuite(TestMessagePYReader))
    suite.addTest(unittest.makeSuite(TestMessageGSReader))
    suite.addTest(unittest.makeSuite(TestMessageZCMLReader))
    return suite

if __name__ == '__main__':
    unittest.main()
