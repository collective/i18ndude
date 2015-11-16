import sys

from lxml import etree

from i18ndude.extract import find_files

GS_NS = "http://namespaces.zope.org/genericsetup"
GS_UPGRADE_DEPENDS = '{%s}upgradeDepends' % GS_NS
GS_UPGRADE_STEP = '{%s}upgradeStep' % GS_NS
GS_UPGRADE_STEPS = '{%s}upgradeSteps' % GS_NS
I18N_DOMAIN = 'i18n_domain'

# These zcml directives should not be translated, because it is not useful.
BLACKLISTED_DIRECTIVES = [
    GS_UPGRADE_DEPENDS,
    GS_UPGRADE_STEP,
    GS_UPGRADE_STEPS,
]
# We cannot really read and interpret the meta zcml to figure out which
# properties are translatable MessageIDs instead of simple TextLines.  So we
# simply take all these properties:
TRANSLATABLE_PROPERTIES = [
    'description',
    'title',
]


class ZCMLParser(object):
    """ZCML profile i18n parser.
    """

    def __init__(self):
        self.catalogs = {}
        self.filename = None

    def parse(self, filename):
        self.filename = filename
        try:
            tree = etree.parse(filename)
        except Exception as e:
            print u"There was an error in parsing %s: %s" % (filename, e)
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
        # We only extract title and description from a registerProfile tag.
        domain = elem.get(I18N_DOMAIN, domain)
        if domain is not None:
            if domain not in self.catalogs:
                self.catalogs[domain] = []
            if elem.tag in BLACKLISTED_DIRECTIVES:
                return
            for key in TRANSLATABLE_PROPERTIES:
                text = elem.get(key)
                if text is not None:
                    text = text.strip()
                if text:
                    msgid = text
                    msgstr = u""
                    self.catalogs[domain].append(
                        (msgid, msgstr,
                         '{}:{}'.format(self.filename, elem.sourceline)))

    def getCatalogs(self):
        return self.catalogs


def zcml_strings(dir, domain="none", exclude=()):
    """Retrieve all messages from `dir` that are in the `domain`.
    """
    parser = ZCMLParser()
    for filename in find_files(dir, '*.zcml', exclude=tuple(exclude)):
        parser.parse(filename)

    return parser.getCatalogs()
