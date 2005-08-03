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
        self.assertEquals(catalog.ORIGINAL_COMMENT, 'Original: ', 'Wrong original comment text')


class TestMessageCatalog(ZopeTestCase.ZopeTestCase):
        
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


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGlobal))
    suite.addTest(makeSuite(TestMessageCatalog))
    return suite

if __name__ == '__main__':
    framework()
