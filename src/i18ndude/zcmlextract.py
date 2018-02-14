import sys

from lxml import etree

from i18ndude.extract import find_files

# Namespaces.
ZOPE_NS = "http://namespaces.zope.org/zope"
GS_NS = "http://namespaces.zope.org/genericsetup"
MONKEY_NS = "http://namespaces.plone.org/monkey"
# Directives using those namespaces.
GS_EXPORT_STEP = '{%s}exportStep' % GS_NS
GS_IMPORT_STEP = '{%s}importStep' % GS_NS
GS_UPGRADE_DEPENDS = '{%s}upgradeDepends' % GS_NS
GS_UPGRADE_STEP = '{%s}upgradeStep' % GS_NS
GS_UPGRADE_STEPS = '{%s}upgradeSteps' % GS_NS
INTERFACE = '{%s}interface' % ZOPE_NS
MONKEY_PATCH = '{%s}patch' % MONKEY_NS
PERMISSION = '{%s}permission' % ZOPE_NS
I18N_DOMAIN = 'i18n_domain'
RULE_TYPE = 'plone.contentrules.rule.interfaces.IRuleEventType'

# These zcml directives should not be translated, because it is not useful.
BLACKLISTED_DIRECTIVES = [
    GS_EXPORT_STEP,
    GS_IMPORT_STEP,
    GS_UPGRADE_DEPENDS,
    GS_UPGRADE_STEP,
    GS_UPGRADE_STEPS,
    MONKEY_PATCH,
    PERMISSION,
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
        # We only extract title and description from a registerProfile tag.
        domain = elem.get(I18N_DOMAIN, domain)
        if domain is not None:
            if domain not in self.catalogs:
                self.catalogs[domain] = []
            if elem.tag in BLACKLISTED_DIRECTIVES:
                return
            if elem.tag == INTERFACE and elem.get('type') == RULE_TYPE:
                self.maybe_add(domain, elem, 'name')
            for key in TRANSLATABLE_PROPERTIES:
                self.maybe_add(domain, elem, key)

    def maybe_add(self, domain, elem, key):
        text = elem.get(key)
        if text is not None:
            text = text.strip()
        if not text:
            return
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
