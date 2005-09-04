# -*- coding: UTF-8 -*-

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from utils import PACKAGE_HOME

try:
    from Products.i18ndude import catalog
except ImportError:
    from i18ndude import catalog

class TestGlobal(ZopeTestCase.ZopeTestCase):

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


class TestMessageEntry(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
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


class TestMessageCatalogInit(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        self.mc = catalog.MessageCatalog
        self.me = catalog.MessageEntry
        self.file = os.path.join(PACKAGE_HOME, 'input', 'test-en.po')
        self.emptyfile = os.path.join(PACKAGE_HOME, 'input', 'empty-en.po')

        self.commentary_header = ['Translation of test.pot to English', 'Hanno Schlichting <schlichting@bakb.net>, 2005']

        self.mimeheader = {'Language-Code': 'en', 'Domain': 'testing', 'PO-Revision-Date': '2005-08-10 21:15+0000', 'Content-Transfer-Encoding': '8bit',
                           'Language-Name': 'English', 'X-Is-Fallback-For': 'en-au en-bz en-ca en-ie en-jm en-nz en-ph en-za en-tt en-gb en-us en-zw',
                           'Plural-Forms': 'nplurals=1; plural=0;', 'Project-Id-Version': 'i18ndude', 'Preferred-Encodings': 'utf-8 latin1',
                           'Last-Translator': 'Unicödé Guy', 'Language-Team': 'Plone i18n <plone-i18n@lists.sourceforge.net>',
                           'POT-Creation-Date': '2005-08-01 12:00+0000', 'Content-Type': 'text/plain; charset=utf-8', 'MIME-Version': '1.0'
                          }

        self.msgids = {'msgid1' : self.me('msgid1', msgstr='msgstr1', references=['file1','file2'], automatic_comments=['excerpt1','excerpt2','excerpt3'], comments=['comment1', 'Original: "msgstr1"']),
                       'msgid2' : self.me('msgid2', msgstr='msgstr2', references=['file2'], automatic_comments=['excerpt2']),
                       'msgid3' : self.me('msgid3', msgstr='msgstr3', references=['file3'], comments=['comment3']),
                       'msgid4' : self.me('msgid4', msgstr='msgstr4', references=['file4']),
                       'msgid5' : self.me('msgid5', msgstr='msgstr5', comments=['comment5']),
                       'msgid6' : self.me('msgid6', msgstr='msgstr6'),
                       'msgid7' : self.me('msgid7', msgstr='msgstr7', comments=[', fuzzy']),
                       'msgid8' : self.me('msgid8', comments=[', fuzzy']),
                       'msgid has spaces' : self.me('msgid has spaces', msgstr='msgstr has spaces', comments=['# I am a dead comment']),
                       'msgid_has_underlines' : self.me('msgid_has_underlines', msgstr='msgstr_has_underlines'),
                       'msgid_has_underlines and spaces' : self.me('msgid_has_underlines and spaces', msgstr='msgstr_has_underlines and spaces'),
                       'msgid for unicode text' : self.me('msgid for unicode text', msgstr='unicode msgstr ···'),
                       'msgid for unicode text with comment' : self.me('msgid for unicode text with comment', msgstr='unicode msgstr ···', references=['./folder/file_unicode'], automatic_comments=['unicode ··· excerpt'], comments=['Original: [···]']),
                       'msgid for text with german umlaut' : self.me('msgid for text with german umlaut', msgstr='äöüß text'),
                       'msgid for text with html-entity' : self.me('msgid for text with html-entity', msgstr='&quot;this&nbsp;is&laquo;&auml;&amp;&ouml;&raquo;&quot;')
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

class TestMessageCatalog(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
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
        self.failUnless(len(self.mc[msgid].references)==4, 'references missing')

    def test_originalComment(self):
        self.mc.add(self.msgid, msgstr=self.msgstr, references=self.references, automatic_comments=self.automatic_comments)
        self.mc[self.msgid].comments.extend(self.comments)
        self.assertEquals(self.mc.getComments(self.msgid), self.comments, 'wrong comments')
        self.assertEquals(self.mc.getOriginalComment(self.msgid), self.orig_comment, 'wrong original comment line')
        self.assertEquals(self.mc.getOriginal(self.msgid), self.orig_text, 'wrong original comment text')
        self.assertEquals(self.mc.getDefaultComment(self.msgid), self.default_comment, 'wrong default comment line')
        self.assertEquals(self.mc.getDefault(self.msgid), self.default_text, 'wrong default comment text')


class TestMessagePoWriter(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        mc = catalog.MessageCatalog
        self.input = os.path.join(PACKAGE_HOME, 'input', 'test-en.po')
        self.output = os.path.join(PACKAGE_HOME, 'output', 'test-en.po')
        self.catalog = mc(filename=self.input)
        if os.path.exists(self.output):
            os.remove(self.output)

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

    def tearDown(self):
        if os.path.exists(self.output):
            os.remove(self.output)


class TestMessagePTReader(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        self.me = catalog.MessageEntry
        filepath = os.path.join(PACKAGE_HOME, 'input', 'test1.pt')
        self.input = [filepath]
        self.output = {u'Buzz': self.me(u'Buzz', msgstr=u'Buzz', references=self.input, automatic_comments=[u'<p i18n:translate="">', u' Buzz', u'</p>']),
                       u'${foo} ${bar}': self.me(u'${foo} ${bar}', msgstr=u'${foo} ${bar}', references=self.input, automatic_comments=[u'<p i18n:translate="">', u' ${foo}', u' ${bar}', u'</p>']),
                       u'Dig this': self.me(u'Dig this', msgstr=u'Dig this', references=self.input, automatic_comments=[u'<input i18n:attributes="value dig_this" type="submit" value="Dig this"/>']),
                       u'text_buzz': self.me(u'text_buzz', msgstr=u'Buzz', references=self.input, automatic_comments=[u'<p i18n:translate="text_buzz">', u' Buzz', u'</p>']),
                       u'some_alt': self.me(u'some_alt', msgstr=u'Some alt', references=self.input, automatic_comments=[u'<img alt="Some alt" i18n:attributes="alt some_alt; title title_some_alt" src="" title="Some title"/>']),
                       u'title_some_alt': self.me(u'title_some_alt', msgstr=u'Some title', references=self.input, automatic_comments=[u'<img alt="Some alt" i18n:attributes="alt some_alt; title title_some_alt" src="" title="Some title"/>'])
                      }

    def test_read(self):
        ptr = catalog.PTReader(self.input)
        ptr.read()
        out = ptr.catalogs['testing']
        for key in out:
            self.failUnless(key in self.output,
                            'Failure in pt parsing.\nUnexpected msgid: %s' % key)
        for key in self.output:
            self.assertEquals(out[key], self.output.get(key),
                              'Failure in pt parsing.\nGot:%s\nExpected:%s' %
                              (out[key], self.output[key]))
        self.assertEqual(len(out), len(self.output))


class TestMessagePYReader(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        self.me = catalog.MessageEntry
        dirpath = os.path.join(PACKAGE_HOME, 'input')
        filepath = os.path.join(dirpath, 'test2.py')
        self.input = dirpath
        self.output = {u'Zero': self.me(u'Zero', references=[filepath]),
                       u'One': self.me(u'One', references=[filepath]),
                       u'Two': self.me(u'Two', references=[filepath]),
                       u'msgid_three': self.me(u'msgid_three', references=[filepath]),
                       u'msgid_four': self.me(u'msgid_four', msgstr='Four ${map}', references=[filepath])
                      }

    def test_read(self):
        pyr = catalog.PYReader(self.input, 'testing')
        pyr.read()
        out = pyr.catalogs['testing']
        for key in self.output:
            self.failUnless(out.get(key, False),
                            'Failure in py parsing.\nMissing:%s' % self.output.get(key))
            self.failUnless(out.get(key) == self.output.get(key),
                            'Failure in py parsing.\nGot:%s\nExpected:%s' %
                            (out.get(key), self.output.get(key)))
        self.assertEqual(len(out), len(self.output))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGlobal))
    suite.addTest(makeSuite(TestMessageEntry))
    suite.addTest(makeSuite(TestMessageCatalogInit))
    suite.addTest(makeSuite(TestMessageCatalog))
    suite.addTest(makeSuite(TestMessagePoWriter))
    suite.addTest(makeSuite(TestMessagePTReader))
    suite.addTest(makeSuite(TestMessagePYReader))
    return suite

if __name__ == '__main__':
    framework()
