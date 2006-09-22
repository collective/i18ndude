# -*- coding: UTF-8 -*-

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from utils import PACKAGE_HOME

from i18ndude import catalog
from i18ndude.visualisation import make_chart

class TestVisualisation(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        self.pot = os.path.join(PACKAGE_HOME, 'input', 'testchart.pot')
        self.po1 = os.path.join(PACKAGE_HOME, 'input', 'testchart-de.po')
        self.po2 = os.path.join(PACKAGE_HOME, 'input', 'testchart-no.po')
        self.po3 = os.path.join(PACKAGE_HOME, 'input', 'testchart-pt-br.po')
        self.out = os.path.join(PACKAGE_HOME, 'output', 'test-chart.gif')
        mc = catalog.MessageCatalog
        self.pot_cat = mc(filename=self.pot)
        self.po_cats = [mc(filename=self.po1), mc(filename=self.po2), mc(filename=self.po3)]
        self.expected = os.path.join(PACKAGE_HOME, 'input', 'test-chart_expected.gif')
        self.expected_values = {'de': 5, 'en': 5, 'pt-br': 2, 'no': 0}

    def test_makeChart(self):
        values = make_chart(self.pot_cat, self.po_cats, self.out, size=(400, 200))
        for lang in self.expected_values:
            self.failUnless(values[lang] == self.expected_values[lang])

    def tearDown(self):
        if os.path.exists(self.out):
            os.remove(self.out)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestVisualisation))
    return suite

if __name__ == '__main__':
    framework()
