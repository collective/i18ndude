import xml.sax

def _translatable(data):
    """Returns 1 for strings that contain alphanumeric characters."""

    for ch in data:
        if ch.isalpha(): return 1
    return 0

def _severity(tag, attrs):
    """Returns empty string if the case may be ignored.
    Returns textual representation of severity otherwise."""

    keys = attrs.keys()
    ns = ':' in tag and '%s:' % tag[:tag.find(':')] or ''
    if ns:
        keys = [ns+key for key in keys]

    if 'metal:use-macro' in keys:
        return ''

    # comments
    elif 'tal:condition' in keys or 'tal:replace' in keys:
        cond_val = attrs.get('tal:condition', attrs.get('condition', None))
        repl_val = attrs.get('tal:replace', attrs.get('replace', None))

        if cond_val == 'nothing' or repl_val == 'nothing':
            return ''

    elif 'tal:replace' in keys or 'tal:content' in keys:
        return 'WARNING'

    else:
        return 'ERROR'


def _valid_i18ned_attr(attr, attrs):
    """This returns 1 for attributes attr that are part of attrs and are
    translated using i18n:attributes. It also returns 1 for any attr that does
    not exist at all in attrs."""

    if attrs.has_key(attr) and _translatable(attrs[attr]):
        if attrs.has_key('i18n:attributes'):
            if attrs['i18n:attributes'].find(';') == -1: # old syntax
                i18nattrs = [i18nattr.strip() for i18nattr in \
                             attrs['i18n:attributes'].split()]
            else:                                        # new syntax
                i18nattrs = [i18nattr.strip().split()[0] for i18nattr in \
                             attrs['i18n:attributes'].split(';') if i18nattr]
            if not (attr in i18nattrs):
                return 0
            else:
                return 1
        else:
            return 0

    return 1


def attr_validator(tag, attrs, logfct):
    """Given a tag and it's attributes' dictionary, this function figures out
    if
       1) Each tag that has a title attribute has it i18ned.
       2) Each image tag has its alt attribute i18ned.
       3) Each tag that is a <input type="submit *or* button"> has its value
          i18ned.
    """

    # 1)
    if not _valid_i18ned_attr('title', attrs):
        logfct('title attribute of <%s> lacks i18n:attributes' % tag,
               'ERROR')

    # 2)
    if tag == 'img':
        if not _valid_i18ned_attr('alt', attrs):
            logfct('alt attribute of <img> lacks i18n:attributes',
                   'ERROR')

    # 3)
    if tag == 'input' and \
              'type' in attrs.keys() and \
              attrs['type'] in ('submit', 'button'):
        if not _valid_i18ned_attr('value', attrs):
            logfct('value attribute of <... submit/button> lacks ' \
                   'i18n:attribute', 'ERROR')


class Handler(xml.sax.ContentHandler):

    def __init__(self, parser, out):
        self._parser = parser
        self._out = out
        self._filename = 'Undefined'

    def log(self, msg, severity):
        """Severity may be one out of 'WARNING', 'ERROR' or 'FATAL'."""
        assert(severity in self._stats.keys())
        self._stats[severity] += 1

    def set_filename(self, filename):
        self._filename = filename

    def startDocument(self):
        self._history = [] # history contains 3-tuples in the form
                           # (tag, attrs, characterdata)
        self._i18nlevel = 0 # 0 means not inside i18n:translate area
        self._stats = {'WARNING':0, 'ERROR':0, 'FATAL':0}

    def endDocument(self):
        pass

    def startElement(self, tag, attrs):
        self._history.append([tag, attrs, ''])

        attr_validator(tag, attrs, self.log)

        if 'i18n:translate' in attrs.keys():
            self._i18nlevel += 1
        elif self._i18nlevel != 0:
            self._i18nlevel += 1

    def endElement(self, tag):
        tag, attrs, data = self._history.pop()
        data = data.strip()

        if _translatable(data):
            if (self._i18nlevel == 0) and not tag in ['script', 'style']: # not enclosed
                severity = _severity(tag, attrs) or ''
                if severity:
                    self.log('i18n:translate missing for this:\n' \
                             '"""\n%s\n"""' % (data,), severity)

        if self._i18nlevel != 0:
            self._i18nlevel -= 1

    def characters(self, data):
        self._history[-1][2] += data


class SilentHandler(Handler):

    def log(self, msg, severity):
        Handler.log(self, msg, severity)

        if severity == 'FATAL':
            print >> self._out, 'Fatal error in document %s' % self._filename
            print >> self._out

    def endDocument(self):
        if not (self._stats['WARNING'] or self._stats['ERROR']):
            return

        print >> self._out, '%s: %s warnings, %s errors' \
              % (self._filename, self._stats['WARNING'], self._stats['ERROR'])
        print >> self._out


class VerboseHandler(Handler):

    def log(self, msg, severity):
        Handler.log(self, msg, severity)

        print >> self._out, \
              '%s:%s:%s:\n-%s- - %s' % (self._filename,
                                        self._parser.getLineNumber(),
                                        self._parser.getColumnNumber(),
                                        severity,
                                        msg)

        if severity == 'FATAL': char = '='
        else: char = '-'
        print >> self._out, char * 79

    def endDocument(self):
        print >> self._out, \
              'Processing of %s finished. (%s warnings, %s errors)' \
              % (self._filename, self._stats['WARNING'], self._stats['ERROR'])
        print >> self._out, '=' * 79


class NoSummaryVerboseHandler(Handler):

    def endElement(self, tag):
        tag, attrs, data = self._history.pop()
        data = data.strip()

        if _translatable(data):
            if (self._i18nlevel == 0) and not tag in ['script', 'style']: # not enclosed
                severity = _severity(tag, attrs) or ''
                if severity and severity != 'WARNING':
                    self.log('i18n:translate missing for this:\n' \
                             '"""\n%s\n"""' % (data,), severity)

        if self._i18nlevel != 0:
            self._i18nlevel -= 1


    def log(self, msg, severity):
        Handler.log(self, msg, severity)

        print >> self._out, \
              '%s:%s:%s:\n-%s- - %s' % (self._filename,
                                        self._parser.getLineNumber(),
                                        self._parser.getColumnNumber(),
                                        severity,
                                        msg)
        print >> self._out

    def endDocument(self):
        pass
