from StringIO import StringIO
import re

# These are included in the file if missing.
DEFAULT_DECL = {
   '<!DOCTYPE':
   '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" ' \
   '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">',

   '<?xml': '<?xml version="1.0" encoding="utf-8"?>'
   }

def prepare_xml(file):
    """Tidies up things within the zpts."""

    content = ''.join(file.readlines())

    for el in ['<!DOCTYPE', '<?xml']:
        idx = content.find(el)
        if idx >= 0:
            if content[0:idx].strip():
                idx2 = content.find('>', idx+1)
                extraction = content[idx:idx2+1]
                content = extraction + content[:idx] + content[idx2+1:]
                # mispositioned element fixed at this point
        else: # element was not found, replace with default
            content = DEFAULT_DECL[el] + content

    # We want namespace declarations for tal, metal and i18n.
    # http://sf.net/tracker/?func=detail&atid=516339&aid=982527&group_id=66950
    mobj = re.search(r'<([a-zA-Z]).*\s', content)
    if mobj:
        if mobj.group(1) == 'html':
            m = mobj.end()
            content = content[:m] + \
            'xmlns:tal="tal" xmlns:i18n="i18n" ' + \
            'xmlns:metal="metal" ' + content[m:]
        else:
            m = mobj.start()
            content = content[:m] + \
            '<html xmlns:tal="tal" xmlns:i18n="i18n" ' + \
            'xmlns:metal="metal">' + content[m:] + '</html>'

    return StringIO(content.strip())


def quote(s):
    """Quote if string has spaces."""

    if [ch for ch in s if ch.isspace()]:
        return '"%s"' % s
    else:
        return s
