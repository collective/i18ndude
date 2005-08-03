import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
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


class TestMessageCatalogInit(ZopeTestCase.ZopeTestCase):

    def test_init(self):
        failing = False
        try:
            test = catalog.MessageCatalog()
        except AssertionError:
            failing = True
        self.failUnless(failing, 'Init without parameters should not be allowed.')

    def test_initWithDomain(self):
        mc = catalog.MessageCatalog
        domain = 'testing'
        test = mc(domain=domain)
        mime = catalog.DEFAULT_PO_MIME
        for key,value in mime:
            if key != 'Domain':
                self.assertEquals(value, test.mime_header[key], 'header mismatch on %s' % key)
            else:
                self.assertEquals(domain, test.mime_header['Domain'], 'Domain mismatch')
        self.assertEquals(catalog.DEFAULT_PO_HEADER, test.commentary_header, 'commentary header mismatch')
        self.assertEquals(len(test), 0, 'Non-empty catalog')

    def test_initWithFilename(self):
        mc = catalog.MessageCatalog
        test = mc(filename='input/demo.pt')
        mime = catalog.DEFAULT_PO_MIME
        for key,value in mime:
            self.assertEquals(value, test.mime_header[key], 'header mismatch on %s' % key)

    def test_initWithFilenameAndDomain(self):
        mc = catalog.MessageCatalog
        failing = False
        try:
            test = mc(domain='testing', filename='input/demo.pt')
        except AssertionError:
            failing = True
        self.failUnless(failing, 'Init with filename and domain parameters is not allowed.')

class TestMessageCatalog(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        self.domain = 'testing'
        self.mc = catalog.MessageCatalog(domain=self.domain)
        self.msgid = 'test msgid'
        self.msgstr = 'test text'
        self.filename = 'test.pt'
        self.excerpt = ['first line', 'second line']
        self.excerpt2 = ['first line2', 'second line2']
        self.orig_text = 'test original'
        self.orig_comment = '%s"%s"' % (catalog.ORIGINAL_COMMENT, self.orig_text)
        self.comment = ['A comment', self.orig_comment]

    def test_add(self):
        msgid = self.msgid
        msgstr = self.msgstr
        filename = self.filename
        excerpt = self.excerpt

        # add with msgid
        self.mc.add(msgid)
        self.failUnless(msgid in self.mc, 'msgid not found in catalog')
        del self.mc[msgid]
        self.failIf(msgid in self.mc, 'msgid found in catalog')
        # add with msgid and msgstr
        self.mc.add(msgid, msgstr=msgstr)
        self.assertEquals(self.mc[msgid][0], msgstr, 'msgstr not found in catalog.')
        del self.mc[msgid]
        self.failIf(msgid in self.mc, 'msgid found in catalog')
        # add with msgid, msgstr and filename
        self.mc.add(msgid, msgstr=msgstr, filename=filename)
        self.assertEquals(self.mc[msgid][1][0][0], filename, 'filename not found in catalog.')
        del self.mc[msgid]
        self.failIf(msgid in self.mc, 'msgid found in catalog')
        # add with msgid, msgstr, filename and excerpt
        self.mc.add(msgid, msgstr=msgstr, filename=filename, excerpt=excerpt)
        self.assertEquals(self.mc[msgid][1][0][1], excerpt, 'excerpt not found in catalog.')
        del self.mc[msgid]
        self.failIf(msgid in self.mc, 'msgid found in catalog')

    def test_multipleAdd(self):
        msgid = self.msgid
        msgstr = self.msgstr
        filename = self.filename
        excerpt = self.excerpt
        excerpt2 = self.excerpt2
        
        self.mc.add(msgid, msgstr=msgstr, filename=filename, excerpt=excerpt)
        self.mc.add(msgid, msgstr=msgstr, filename=filename, excerpt=excerpt)
        self.failUnless(len(self.mc)==1, 'duplicate msgid')
        self.failUnless(len(self.mc[msgid][1])==2, 'second occurrence missing')
        self.mc.addToSameFileName(msgid, msgstr=msgstr, filename=filename, excerpt=excerpt)
        self.failUnless(len(self.mc[msgid][1][1][1])==2, 'duplicate occurrence')
        self.mc.addToSameFileName(msgid, msgstr=msgstr, filename=filename, excerpt=excerpt2)
        self.failUnless(len(self.mc[msgid][1][1][1])==4, 'new occurrence missing')

    def test_originalComment(self):
        self.mc.add(self.msgid, msgstr=self.msgstr, filename=self.filename, excerpt=self.excerpt)
        self.mc[self.msgid][2].extend(self.comment)
        self.assertEquals(self.mc.get_comment(self.msgid), self.comment, 'wrong comment')
        self.assertEquals(self.mc.get_original_comment(self.msgid), self.orig_comment, 'wrong original comment line')
        self.assertEquals(self.mc.get_original(self.msgid), self.orig_text, 'wrong original comment text')



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGlobal))
    suite.addTest(makeSuite(TestMessageCatalogInit))
    suite.addTest(makeSuite(TestMessageCatalog))
    return suite

if __name__ == '__main__':
    framework()
