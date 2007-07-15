# -*- coding: UTF-8 -*-

import os, unittest
from unittest import makeSuite

from utils import PACKAGE_HOME

from i18ndude import catalog

class TestGlobal(unittest.TestCase):

    def test_isLiteralId(self):
        i = catalog.is_literal_id
        errortext = 'False literal msgid recognition'
        self.failIf(i('label_yes'), errortext)
        self.failIf(i('_'), errortext)
        self.failUnless(i(' '), errortext)
        self.failUnless(i(' _'), errortext)
        self.failUnless(i('text'), errortext)
        self.failUnless(i('This is a text.'), errortext)

    def test_originalComment(self):
        self.assertEquals(catalog.ORIGINAL_COMMENT, 'Original: ', 'Wrong original comment constant')
        
    def test_defaultComment(self):
        self.assertEquals(catalog.DEFAULT_COMMENT, 'Default: ', 'Wrong default comment constant')


class TestMessageEntry(unittest.TestCase):

    def setUp(self):
        self.me = catalog.MessageEntry
        self.msgid = 'test msgid'
        self.msgstr = 'test text'
        self.references = ['test1.pt', 'test2.pt']
        self.default_text = 'test default'
        self.default_comment = '%s"%s"' % (catalog.DEFAULT_COMMENT, self.default_text)
        self.automatic_comments = ['first line', 'second line', self.default_comment]
        self.orig_text = 'test original'
        self.orig_comment = '%s"%s"' % (catalog.ORIGINAL_COMMENT, self.orig_text)
        self.comments = ['A comment', self.orig_comment]

    def test_init(self):
        me = self.me
        me1 = me(self.msgid)
        self.assertEquals(me1.msgid, self.msgid, 'msgid not set correctly')
        me1 = me(self.msgid, msgstr=self.msgstr)
        self.assertEquals(me1.msgid, self.msgid, 'msgid not set correctly')
        self.assertEquals(me1.msgstr, self.msgstr, 'msgstr not set correctly')

        me1 = me(self.msgid, msgstr=self.msgstr, references=self.references)
        self.assertEquals(me1.msgid, self.msgid, 'msgid not set correctly')
        self.assertEquals(me1.msgstr, self.msgstr, 'msgstr not set correctly')
        self.assertEquals(me1.references, self.references, 'references not set correctly')

        me1 = me(self.msgid, msgstr=self.msgstr, comments=self.comments)
        self.assertEquals(me1.msgid, self.msgid, 'msgid not set correctly')
        self.assertEquals(me1.msgstr, self.msgstr, 'msgstr not set correctly')
        self.assertEquals(me1.comments, self.comments, 'comments not set correctly')
        self.assertEquals(me1.getOriginalComment(), self.orig_comment, \
                          'Original comment not set correctly')
        self.assertEquals(me1.getOriginal(), self.orig_text, \
                          'Original text not set correctly')

        me2 = me(self.msgid, msgstr=self.msgstr, automatic_comments=self.automatic_comments)
        self.assertEquals(me2.msgid, self.msgid, 'msgid not set correctly')
        self.assertEquals(me2.msgstr, self.msgstr, 'msgstr not set correctly')
        self.assertEquals(me2.automatic_comments, self.automatic_comments, 'comments not set correctly')
        self.assertEquals(me2.getDefaultComment(), self.default_comment, \
                          'Default comment not set correctly')
        self.assertEquals(me2.getDefault(), self.default_text, \
                          'Default text not set correctly')


class TestMessageCatalogInit(unittest.TestCase):

    def setUp(self):
        self.mc = catalog.MessageCatalog
        self.me = catalog.MessageEntry
        self.file = os.path.join(PACKAGE_HOME, 'input', 'test-en.po')
        self.emptyfile = os.path.join(PACKAGE_HOME, 'input', 'empty-en.po')

        self.commentary_header = ['Translation of test.pot to English', 'Hanno Schlichting <schlichting@bakb.net>, 2005']

        self.mimeheader = {'Language-Code': 'en',
                           'Domain': 'testing',
                           'PO-Revision-Date': '2005-08-10 21:15+0000',
                           'Content-Transfer-Encoding': '8bit',
                           'Language-Name': 'English',
                           'Plural-Forms': 'nplurals=1; plural=0;',
                           'Project-Id-Version': 'i18ndude',
                           'Preferred-Encodings': 'utf-8 latin1',
                           'Last-Translator': 'Unicödé Guy',
                           'Language-Team': 'Plone i18n <plone-i18n@lists.sourceforge.net>',
                           'POT-Creation-Date': '2005-08-01 12:00+0000',
                           'Content-Type': 'text/plain; charset=utf-8', 'MIME-Version': '1.0'
                          }

        self.msgids = {u'msgid1' : self.me('msgid1', msgstr='msgstr1', references=['file1','file2'], automatic_comments=['Default: "msgstr1"'], comments=['comment1']),
                       u'msgid2' : self.me('msgid2', msgstr='msgstr2', references=['file2']),
                       u'msgid3' : self.me('msgid3', msgstr='\\n\\nmsgstr\\n3', references=['file3'], comments=['comment3']),
                       u'msgid4' : self.me('msgid4', msgstr='msgstr4', references=['file4']),
                       u'msgid5' : self.me('msgid5', msgstr='msgstr5', comments=['comment5']),
                       u'msgid6' : self.me('msgid6', msgstr='msgstr6'),
                       u'msgid7' : self.me('msgid7', msgstr='msgstr7', comments=[', fuzzy']),
                       u'msgid8' : self.me('msgid8'),
                       u'msgid has spaces' : self.me('msgid has spaces', msgstr='msgstr has spaces', comments=['# I am a dead comment']),
                       u'msgid_has_underlines' : self.me('msgid_has_underlines', msgstr='msgstr_has_underlines'),
                       u'msgid_has_underlines and spaces' : self.me('msgid_has_underlines and spaces', msgstr='msgstr_has_underlines and spaces'),
                       u'msgid for unicode text' : self.me('msgid for unicode text', msgstr=u'unicode msgstr \xb7\xb7\xb7'),
                       u'msgid for unicode text with comment' : self.me('msgid for unicode text with comment', msgstr=u'unicode msgstr \xb7\xb7\xb7', references=['./folder/file_unicode'], automatic_comments=['Default: [···]']),
                       u'msgid for text with german umlaut' : self.me('msgid for text with german umlaut', msgstr=u'\xe4\xf6\xfc\xdf text'),
                       u'msgid for text with html-entity' : self.me('msgid for text with html-entity', msgstr='&quot;this&nbsp;is&laquo;&auml;&amp;&ouml;&raquo;&quot;')
                      }

    def test_init(self):
        failing = False
        try:
            test = catalog.MessageCatalog()
        except AssertionError:
            failing = True
        self.failUnless(failing, 'Init without parameters should not be allowed.')

    def test_initWithDomain(self):
        domain = 'testing'
        test = self.mc(domain=domain)
        mime = catalog.DEFAULT_PO_MIME
        for key,value in mime:
            if key != 'Domain':
                self.assertEquals(value, test.mime_header[key], 'header mismatch on %s' % key)
            else:
                self.assertEquals(domain, test.mime_header['Domain'], 'Domain mismatch')
        self.assertEquals(catalog.DEFAULT_PO_HEADER, test.commentary_header, 'commentary header mismatch')
        self.assertEquals(len(test), 0, 'Non-empty catalog')

    def test_initWithEmptyFile(self):
        test = self.mc(filename=self.emptyfile)
        mime = catalog.DEFAULT_PO_MIME
        for key,value in mime:
            self.assertEquals(value, test.mime_header[key], 'header mismatch on %s' % key)

    def test_initWithEmptyFileAndDomain(self):
        failing = False
        try:
            test = self.mc(domain='testing', filename=self.emptyfile)
        except AssertionError:
            failing = True
        self.failUnless(failing, 'Init with filename and domain parameters is not allowed.')

    def test_initWithFile(self):
        test = self.mc(filename=self.file)
        for key in test.mime_header:
            self.assertEquals(test.mime_header[key], self.mimeheader[key], 'wrong mime header parsing:\nGot: %s !=\nExpected: %s' % (test.mime_header[key], self.mimeheader[key]))
        for value in test.commentary_header:
            self.failUnless(value in self.commentary_header, 'wrong commentary header parsing')
        if not test == self.msgids:
            for key in test:
                self.failUnless(test[key] == self.msgids[key], 'error in po parsing:\n Got: %s !=\nExpected: %s' % (test[key], self.msgids[key]))

class TestMessageCatalog(unittest.TestCase):

    def setUp(self):
        self.domain = 'testing'
        self.mc = catalog.MessageCatalog(domain=self.domain)
        self.msgid = 'test msgid'
        self.msgstr = 'test text'
        self.references = ['test1.pt', 'test2.pt']
        self.default_text = 'test default'
        self.default_comment = '%s"%s"' % (catalog.DEFAULT_COMMENT, self.default_text)
        self.automatic_comments = ['first line', 'second line', self.default_comment]
        self.orig_text = 'test original'
        self.orig_comment = '%s"%s"' % (catalog.ORIGINAL_COMMENT, self.orig_text)
        self.comments = ['A comment', self.orig_comment]

    def test_add(self):
        msgid = self.msgid
        msgstr = self.msgstr
        references = self.references
        automatic_comments = self.automatic_comments

        # add with msgid
        self.mc.add(msgid)
        self.failUnless(msgid in self.mc, 'msgid not found in catalog')
        del self.mc[msgid]
        self.failIf(msgid in self.mc, 'msgid found in catalog')
        # add with msgid and msgstr
        self.mc.add(msgid, msgstr=msgstr)
        self.assertEquals(self.mc[msgid].msgstr, msgstr, 'msgstr not found in catalog.')
        del self.mc[msgid]
        self.failIf(msgid in self.mc, 'msgid found in catalog')
        # add with msgid, msgstr and filename
        self.mc.add(msgid, msgstr=msgstr, references=references)
        self.assertEquals(self.mc[msgid].references, references, 'references not found in catalog.')
        del self.mc[msgid]
        self.failIf(msgid in self.mc, 'msgid found in catalog')
        # add with msgid, msgstr, filename and excerpt
        self.mc.add(msgid, msgstr=msgstr, references=references, automatic_comments=automatic_comments)
        self.assertEquals(self.mc[msgid].automatic_comments, automatic_comments, 'automatic_comments not found in catalog.')
        del self.mc[msgid]
        self.failIf(msgid in self.mc, 'msgid found in catalog')

    def test_multipleAdd(self):
        msgid = self.msgid
        msgstr = self.msgstr
        references = self.references
        automatic_comments = self.automatic_comments

        self.mc.add(msgid, msgstr=msgstr, references=references, automatic_comments=automatic_comments)
        self.mc.add(msgid, msgstr=msgstr, references=references, automatic_comments=automatic_comments)
        self.failUnless(len(self.mc)==1, 'duplicate msgid')
        self.failUnless(len(self.mc[msgid].references)==2, 'references missing')

    def test_originalComment(self):
        self.mc.add(self.msgid, msgstr=self.msgstr, references=self.references, automatic_comments=self.automatic_comments)
        self.mc[self.msgid].comments.extend(self.comments)
        self.assertEquals(self.mc.getComments(self.msgid), self.comments, 'wrong comments')
        self.assertEquals(self.mc.getOriginalComment(self.msgid), self.orig_comment, 'wrong original comment line')
        self.assertEquals(self.mc.getOriginal(self.msgid), self.orig_text, 'wrong original comment text')
        self.assertEquals(self.mc.getDefaultComment(self.msgid), self.default_comment, 'wrong default comment line')
        self.assertEquals(self.mc.getDefault(self.msgid), self.default_text, 'wrong default comment text')

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
        self.failUnless(len(self.pot)==len(self.po), 'number of messages does not match')
        for msgid in self.pot:
            self.failUnless(msgid in self.po, 'msgid %s could not be found' % self.pot[msgid])
            self.failUnless(self.po[msgid].references == self.pot[msgid].references)
            defaults = self.po[msgid].getDefaults()
            if defaults is not None:
                for dc in defaults:
                    self.failUnless(dc == self.pot[msgid].getDefault() or
                                    dc == old_defaults[msgid], 'Either old or new default comment is missing on msgid: %s' % msgid)

class TestMessagePoWriter(unittest.TestCase):

    def setUp(self):
        mc = catalog.MessageCatalog
        self.input = os.path.join(PACKAGE_HOME, 'input', 'test-en.po')
        self.output = os.path.join(PACKAGE_HOME, 'output', 'test-en.po')
        self.input2 = os.path.join(PACKAGE_HOME, 'input', 'test2-en.po')
        self.expectedOutput2 = os.path.join(PACKAGE_HOME, 'input', 'test2_expected-en.po')
        self.output2 = os.path.join(PACKAGE_HOME, 'output', 'test2-en.po')
        self.catalog = mc(filename=self.input)
        self.catalog2 = mc(filename=self.input2)
        if os.path.exists(self.output):
            os.remove(self.output)
        if os.path.exists(self.output2):
            os.remove(self.output2)

    def test_write(self):
        fd = open(self.output, 'wb')
        pow = catalog.POWriter(fd, self.catalog)
        pow.write(sort=True)
        fd.close()

        input = open(self.input, 'r')
        output = open(self.output, 'r')

        # compare line by line
        inlines = input.readlines()
        outlines = enumerate(output.readlines())

        input.close()
        output.close()

        for i, result in outlines:
            orig = inlines[i]
            self.failUnlessEqual(orig, result, 'difference in line %s, \'%s\' != \'%s\'' % (i, orig, result))

    def test_writeSpecialComments(self):
        fd = open(self.output2, 'wb')
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
            self.failUnlessEqual(orig, result, 'difference in line %s, Got: \'%s\' != Expected: \'%s\'' % (i, orig, result))

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
        self.output = {u'Buzz': self.me(u'Buzz', msgstr=u'Buzz', references=[filename+':18']),
                       u'${foo} ${bar}': self.me(u'${foo} ${bar}', msgstr=u'${foo} ${bar}', references=[filename+':23']),
                       u'dig_this': self.me(u'dig_this', msgstr=u'Dig this', references=[filename+':49']),
                       u'text_buzz': self.me(u'text_buzz', msgstr=u'Buzz', references=[filename+':26']),
                       u'some_alt': self.me(u'some_alt', msgstr=u'Some alt', references=[filename+':12']),
                       u'title_some_alt': self.me(u'title_some_alt', msgstr=u'Some title', references=[filename+':12']),
                       u'Job started at ${datetime} by user ${userid}.': self.me(u'Job started at ${datetime} by user ${userid}.', msgstr=u'Job started at ${datetime} by user ${userid}.', references=[filename+':43']),
                       u'spacing': self.me(u'spacing', msgstr=u'Space <br /> before and after.', references=[filename+':34']),
                       u'spacing_strong': self.me(u'spacing_strong', msgstr=u'Please press your browser\'s <strong>Back</strong> button to try again.', references=[filename+':38']),
                       u'<tt>domain</tt> is one of the <em>local domains</em>:': self.me(u'<tt>domain</tt> is one of the <em>local domains</em>:', msgstr='<tt>domain</tt> is one of the <em>local domains</em>:', references=[filename+':46'])
                      }

    def test_read(self):
        ptr = catalog.PTReader(self.input, domain='testing')
        ptr.read()
        out = ptr.catalogs['testing']
        for key in out:
            self.failUnless(key in self.output,
                            'Failure in pt parsing.\nUnexpected msgid: %s' % key)
        for key in self.output:
            self.failUnless(out[key] == self.output[key],
                              'Failure in pt parsing.\nGot:%s\nExpected:%s' %
                              (out[key], self.output[key]))
        self.assertEqual(len(out), len(self.output))


class TestMessagePYReader(unittest.TestCase):

    def setUp(self):
        self.me = catalog.MessageEntry
        dirpath = os.path.join(PACKAGE_HOME, 'input')
        filepath = os.path.join(dirpath, 'test2.py')
        self.input = dirpath
        self.output = {u'Zero': self.me(u'Zero', references=[filepath+':3']),
                       u'One': self.me(u'One', references=[filepath+':4']),
                       u'msgid_three': self.me(u'msgid_three', msgstr='Three', references=[filepath+':9']),
                       u'msgid_four': self.me(u'msgid_four', msgstr='Four ${map}', references=[filepath+':12']),
                       # XXX This should not be found as it's in a different domain
                       # instead it recognizes the domain as a msgstr now
                       u'Out1': self.me(u'Out1', msgstr='running', references=[filepath+':6'])
                      }

    def test_read(self):
        pyr = catalog.PYReader(self.input, 'testing')
        pyr.read()
        out = pyr.catalogs['testing']
        for key in out:
            self.failUnless(key in self.output,
                            'Failure in py parsing.\nUnexpected msgid: %s' % key)
        for key in self.output:
            self.failUnless(out.get(key, False),
                            'Failure in py parsing.\nMissing:%s' % self.output.get(key))
            self.failUnless(out.get(key) == self.output.get(key),
                            'Failure in py parsing.\nGot:%s\nExpected:%s' %
                            (out.get(key), self.output.get(key)))
        self.assertEqual(len(out), len(self.output))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(makeSuite(TestGlobal))
    suite.addTest(makeSuite(TestMessageEntry))
    suite.addTest(makeSuite(TestMessageCatalogInit))
    suite.addTest(makeSuite(TestMessageCatalog))
    suite.addTest(makeSuite(TestMessageCatalogSync))
    suite.addTest(makeSuite(TestMessagePoWriter))
    suite.addTest(makeSuite(TestMessagePTReader))
    suite.addTest(makeSuite(TestMessagePYReader))
    return suite

if __name__ == '__main__':
    unittest.main()
