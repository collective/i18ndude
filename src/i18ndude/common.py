from lxml import etree
from io import StringIO
import re

import sys
PY3 = sys.version_info > (3,)
if PY3:
    unicode = str

# These are included in the file if missing.
DEFAULT_DECL = {
    '<!DOCTYPE':
    '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" '
    '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">',

    '<?xml': '<?xml version="1.0" encoding="utf-8"?>'
}
HTML_PARSER = etree.HTMLParser()


def prepare_xml(file):
    """Tidies up things within the zpts."""

    content = ''.join(file.readlines())

    for el in ['<!DOCTYPE', '<?xml']:
        idx = content.find(el)
        if idx >= 0:
            if content[0:idx].strip():
                idx2 = content.find('>', idx + 1)
                extraction = content[idx:idx2 + 1]
                content = extraction + content[:idx] + content[idx2 + 1:]
                # mispositioned element fixed at this point
        else:  # element was not found, replace with default
            content = DEFAULT_DECL[el] + content

    # We want namespace declarations for tal, metal and i18n.
    # http://sf.net/tracker/?func=detail&atid=516339&aid=982527&group_id=66950
    mobj = re.search(r'<([a-zA-Z]+)', content)
    if mobj:
        if mobj.group(1) == 'html':
            m = mobj.end()
            extra = ''
            if 'xmlns:i18n=' not in content:
                extra += 'xmlns:i18n="http://xml.zope.org/namespaces/i18n" '
            if 'xmlns:metal=' not in content:
                extra += 'xmlns:metal="http://xml.zope.org/namespaces/metal" '
            if 'xmlns:tal=' not in content:
                extra += 'xmlns:tal="http://xml.zope.org/namespaces/tal">'
            if extra:
                content = content[:m] + ' ' + extra + content[m:]
        else:
            m = mobj.start()
            content = (
                content[:m] +
                '<html ' +
                'xmlns:i18n="http://xml.zope.org/namespaces/i18n" '
                'xmlns:metal="http://xml.zope.org/namespaces/metal" ' +
                'xmlns:tal="http://xml.zope.org/namespaces/tal">' +
                '<head><title></title></head><body>' +
                content[m:] +
                '</body></html>')

    return StringIO(unicode(content.strip()))


def tree_content(tree):
    content = etree.tostring(tree).decode()
    if content is None:
        return
    return StringIO(content.strip())


def present_file_contents(filename):
    """Present the file in various ways.

    It is hard to parse files that may be plain html, plain xml, or a
    page template.  It does not help that the page template might miss
    namespaces so it gives an xml parse error.  Or it has html5-style
    attributes that cannot be parsed by xml.sax but need to be smoothed
    over by an html parser.  And this html parser may introduce double
    attributes, like adding an xml:lang when this is already there in
    the original template.

    So we we present the file in various way, that other code can
    iterate over.
    """
    errors = []
    # First try our (t)rusty old way, as that reports the original line
    # numbers.
    with open(filename) as fh:
        yield prepare_xml(fh)
    # Then try to parse as nice xml.
    # If that fails, try to parse it as html.
    for parser in (None, HTML_PARSER):
        try:
            tree = etree.parse(filename, parser)
        except etree.XMLSyntaxError as error:
            errors.append(error)
        else:
            yield tree_content(tree)
    # Give back any errors we found.
    yield errors
