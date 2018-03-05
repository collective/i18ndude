import sys

from lxml import etree

from i18ndude.extract import find_files

I18N_NS = 'http://xml.zope.org/namespaces/i18n'
I18N_DOMAIN = '{%s}domain' % I18N_NS
I18N_TRANSLATE = '{%s}translate' % I18N_NS
I18N_ATTRIBUTES = '{%s}attributes' % I18N_NS


class GSParser(object):
    """GenericSetup profile i18n parser.
    """

    def __init__(self):
        self.catalogs = {}
        self.filename = None

    def parse(self, filename):
        self.filename = filename
        try:
            tree = etree.parse(filename)
        except Exception as e:
            print(u"There was an error in parsing %s: %s" % (filename, e))
            sys.exit(0)
        elem = tree.getroot()
        domain = elem.get(I18N_DOMAIN, None)
        self.parseNode(elem, domain)
        self.parseChildren(elem, domain)

    def parseChildren(self, elem, domain):
        domain = elem.get(I18N_DOMAIN, domain)
        for child in elem.getchildren():
            self.parseNode(child, domain)
            self.parseChildren(child, domain)

    def parseNode(self, elem, domain):
        domain = elem.get(I18N_DOMAIN, domain)
        translate = elem.get(I18N_TRANSLATE)
        attributes = elem.get(I18N_ATTRIBUTES)
        if domain is not None:
            if domain not in self.catalogs:
                self.catalogs[domain] = []
            if translate is not None:
                text = elem.text
                if text is not None:
                    text = text.strip()
                if text:
                    msgid = msgstr = text
                    if translate:
                        msgid = translate
                    else:
                        msgstr = u""
                    if msgid:
                        self.catalogs[domain].append(
                            (msgid, msgstr, self.filename))
            if attributes is not None:
                attributes = attributes.strip().split(';')
                for attr in attributes:
                    parts = attr.split()
                    if len(parts) == 2:
                        attr, msgid = parts
                    else:
                        attr = parts[0]
                        msgid = u""
                    text = elem.get(attr)
                    if text is not None:
                        text = text.strip()
                    if text:
                        if msgid:
                            msgstr = text
                        else:
                            msgid = text
                            msgstr = u""
                        self.catalogs[domain].append(
                            (msgid, msgstr, self.filename))

    def getCatalogs(self):
        return self.catalogs


def gs_strings(dir, domain="none", exclude=()):
    """Retrieve all messages from `dir` that are in the `domain`.
    """
    parser = GSParser()
    for filename in find_files(dir, '*.xml', exclude=tuple(exclude)):
        parser.parse(filename)

    return parser.getCatalogs()
