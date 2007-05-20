import sys

try:
    from xml.etree.ElementTree import ElementTree
except ImportError:
    from elementtree.ElementTree import ElementTree

from i18ndude.extract import find_files
I18N_DOMAIN = '{http://xml.zope.org/namespaces/i18n}domain'
I18N_TRANSLATE = '{http://xml.zope.org/namespaces/i18n}translate'

class GSParser(object):
    """GenericSetup profile i18n parser."""

    def __init__(self):
        self.catalogs = {}
        self.filename = None

    def parse(self, filename):
        self.filename = filename
        tree = ElementTree(file=filename)
        elem = tree.getroot()
        domain = elem.get(I18N_DOMAIN, None)
        self.parseChildren(elem, domain)

    def parseChildren(self, elem, domain):
        for child in elem.getchildren():
            domain = child.get(I18N_DOMAIN, domain)
            translate = child.get(I18N_TRANSLATE)
            if domain is not None and translate is not None:
                name = child.get('name')
                msgid = msgstr = child.text
                if translate:
                    msgid = translate
                if domain not in self.catalogs:
                    self.catalogs[domain] = []
                if msgid is not None:
                    self.catalogs[domain].append((msgid, msgstr, self.filename, name))
            self.parseChildren(child, domain)

    def getCatalogs(self):
        return self.catalogs


def gs_strings(dir, domain="none", exclude=()):
    """Retrieve all messages from `dir` that are in the `domain`.
    """
    parser = GSParser()
    for filename in find_files(dir, '*.xml', exclude=tuple(exclude)):
        parser.parse(filename)

    return parser.getCatalogs()
