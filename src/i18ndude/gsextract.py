import sys

try:
    from xml.etree.ElementTree import ElementTree
except ImportError:
    from elementtree.ElementTree import ElementTree

from i18ndude.extract import find_files

I18N_NS = 'http://xml.zope.org/namespaces/i18n'
I18N_DOMAIN = '{%s}domain' % I18N_NS
I18N_TRANSLATE = '{%s}translate' % I18N_NS
I18N_ATTRIBUTES = '{%s}attributes' % I18N_NS


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
            attributes = child.get(I18N_ATTRIBUTES)
            if domain is not None:
                if domain not in self.catalogs:
                    self.catalogs[domain] = []
                if translate is not None:
                    name = child.get('name')
                    msgid = msgstr = child.text
                    if translate:
                        msgid = translate
                    if msgid:
                        self.catalogs[domain].append((msgid, msgstr, self.filename))
                if attributes is not None:
                    # TODO Support for explicit msgids...
                    attributes = attributes.strip().split(';')
                    for attr in attributes:
                        attr = attr.strip()
                        msgid = msgstr = child.get(attr)
                        if msgid:
                            self.catalogs[domain].append((msgid, msgstr, self.filename))
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
