import re, sys, time

from zope.i18nmessageid import Message

import common
from odict import odict

DEFAULT_PO_HEADER = [
    '--- PLEASE EDIT THE LINES BELOW CORRECTLY ---',
    'SOME DESCRIPTIVE TITLE.',
    'FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.']

DEFAULT_PO_MIME = (('Project-Id-Version', 'PACKAGE VERSION'),
                   ('POT-Creation-Date', 'YEAR-MO-DA HO:MI +ZONE'),
                   ('PO-Revision-Date', 'YEAR-MO-DA HO:MI +ZONE'),
                   ('Last-Translator', 'FULL NAME <EMAIL@ADDRESS>'),
                   ('Language-Team', 'LANGUAGE <LL@li.org>'),
                   ('MIME-Version', '1.0'),
                   ('Content-Type', 'text/plain; charset=utf-8'),
                   ('Content-Transfer-Encoding', '8bit'),
                   ('Plural-Forms', 'nplurals=1; plural=0'),
                   ('Language-Code', 'en'),
                   ('Language-Name', 'English'),
                   ('Preferred-Encodings', 'utf-8 latin1'),
                   ('Domain', 'DOMAIN'))

MAX_OCCUR = 3 # maximum number of occurrences listed

ORIGINAL_COMMENT = 'Original: '
DEFAULT_COMMENT = 'Default: '

def now():
    fmt = '%Y-%m-%d %H:%M+0000'
    return time.strftime(fmt, time.gmtime())

def is_literal_id(msgid):
    if '_' in msgid and not ' ' in msgid: return False
    else: return True

class MessageEntry:
    """ MessageEntry is class representing one msgid with its accompanying
    msgstr and optional positional information and comments.
    """
    
    def __init__(self, msgid, msgstr='', references=[], automatic_comments=[], comments=[]):
        """ Build a MessageEntry"""
        self.msgid = msgid
        self.msgstr = msgstr
        self.references = references
        self.automatic_comments = automatic_comments
        self.comments = comments

    def __repr__(self):
        """ Textual representation of a MessageEntry"""
        return ', '.join([self.msgid, self.msgstr, repr(self.references), repr(self.automatic_comments), repr(self.comments)])

    def __eq__(self, other):
        """ Compare a MessageEntry to another one"""
        assert isinstance(other, MessageEntry)
        if self.msgid == other.msgid and self.msgstr == other.msgstr and \
           self.references == other.references and self.automatic_comments == \
           other.automatic_comments and self.comments == other.comments:
           return True
        return False

    def __ne__(self, other):
        """ Compare a MessageEntry to another one"""
        assert isinstance(other, MessageEntry)
        if self.__eq__(other):
           return False
        return True

    def getDefaultComment(self, multiple=False):
        """Returns the automatic comment starting with Default: """
        defaults = []
        for c in self.automatic_comments:
            if c.startswith(DEFAULT_COMMENT):
                defaults.append(c)
        if len(defaults) == 0:
            return None
        if multiple:
            return defaults
        return defaults[0]

    def getDefault(self):
        """Returns the text of the default comment"""
        comment = self.getDefaultComment()
        if comment is not None:
            default = comment.replace(DEFAULT_COMMENT+'\"','')
            return default[:-1]
        return None

    def getDefaults(self):
        """Returns the text of the default comments"""
        comments = self.getDefaultComment(multiple=True)
        defaults = []
        if comments is None:
            return None
        for dc in comments:
            default = dc.replace(DEFAULT_COMMENT+'\"','')
            defaults.append(default[:-1])
        return defaults

    def getOriginalComment(self):
        """Returns the comment line starting with Original: """
        for c in self.comments:
            if c.startswith(ORIGINAL_COMMENT):
                return c
        return None

    def getOriginal(self):
        """Returns the text of the original comment"""
        comment = self.getOriginalComment()
        if comment is not None:
            orig = comment.replace(ORIGINAL_COMMENT+'\"','')
            return orig[:-1]
        return None


class MessageCatalog(odict):
    """MessageCatalog is a collection of MessageEntries

    If we're reading in from a .po-file, MessageCatalog also contains an
    individual MIME-Header and a domain. While a default MIME-Header is
    available, a domain must always be supplied.

    MessageCatalog's dictionary maps msgids to information that is available
    for those. The values in this dictionary are of the type MessageEntry.
    """

    def __init__(self, filename=None, domain=None):
        """Build a MessageCatalog, either by reading from a .po-file or
        specifying a domain."""
        odict.__init__(self)

        # XOR
        assert not (filename and domain)
        assert filename or domain

        self.commentary_header = DEFAULT_PO_HEADER
        self.mime_header = odict()
        for key, value in DEFAULT_PO_MIME:
            self.mime_header[key] = value

        self.filename = filename
        self.domain = domain

        if filename:
            self._initialize_with(filename)
        elif domain:
            self.mime_header['Domain'] = domain

    def getComments(self, msgid):
        """Returns the commentary lines that I have for a msgid."""
        assert msgid in self
        return self[msgid].comments

    def getOriginalComment(self, msgid):
        """Returns the original comment for a msgid."""
        assert msgid in self
        return self[msgid].getOriginalComment()

    def getOriginal(self, msgid):
        """Returns the original text for a msgid."""
        assert msgid in self
        return self[msgid].getOriginal()

    def getDefaultComment(self, msgid):
        """Returns the original comment for a msgid."""
        assert msgid in self
        return self[msgid].getDefaultComment()

    def getDefault(self, msgid):
        """Returns the original text for a msgid."""
        assert msgid in self
        return self[msgid].getDefault()

    def add(self, msgid, msgstr='', comments=[], references=[], automatic_comments=[]):
        """Add a entry into the catalogue.

        If the msgid already exists in my catalog, I will only add comment,
        reference and automatic comments to the entry if these doesn't exist yet"""
        if not self.has_key(msgid):
            self[msgid] = MessageEntry(msgid, msgstr=msgstr, comments=comments,
                                       references=references,
                                       automatic_comments=automatic_comments)
        else:
            if comments:
                comments = [c for c in comments if c not in self[msgid].comments]
                self[msgid].comments.extend(comments)
            if references:
                references = [ref for ref in references
                              if ref not in self[msgid].references]
                self[msgid].references.extend(references)
            if automatic_comments:
                automatic_comments = [ac for ac in automatic_comments if ac
                                      not in self[msgid].automatic_comments]
                self[msgid].automatic_comments.extend(automatic_comments)

    def add_missing(self, msgctl, defaultmsgstr='', mergewarn=None):
        """Each msgid that I miss and ``msgctl`` contains will be included in
        my catalog, including contextual information.

        Note that the msgstr is set to be the empty string by default, but
        you can override what's filled in by providing a defaultmsgstr arg.

        The original msgstr is never copied. Therefore the contextual
        information (i.e. lines that start with '#') must contain the string
        that is to be translated in order to make sense to the translator.

        Returns the ids that were added."""
        ids = []
        for key in msgctl.keys():
            if not self.has_key(key):
                entry = msgctl[key]
                msgstr = defaultmsgstr
                if isinstance(key, Message):
                    msgstr = key.default or msgstr
                self.add(key, msgstr=msgstr, comments=entry.comments,
                         references=entry.references,
                         automatic_comments=entry.automatic_comments)
                ids.append(key)
            elif mergewarn:
                print >> sys.stderr, \
                    'Merge-Warning: Key is already in target-catalog: %s' % key

        return ids

    def merge(self, msgctl):
        """Each msgid that I miss and ``msgctl`` contains will be included in
        my catalog."""
        for key in msgctl.keys():
            if not self.has_key(key):
                entry = msgctl[key]
                self.add(key, msgstr=entry.msgstr, comments=entry.comments,
                              references=entry.references,
                              automatic_comments=entry.automatic_comments)

    def sync(self, msgctl):
        """Syncronize the catalog with the given one. This removes all messages
        which are not found anymore in the new catalog, adds additional ones and
        overwrites the comments with the ones from the given catalog. This is
        used in the sync command.
        """
        removed_msgids = [common.quote(msgid)
                          for msgid in self.accept_ids(msgctl.keys())]
        self.overwrite_context(msgctl)
        added_msgids = [common.quote(msgid)
                        for msgid in self.add_missing(msgctl)]

        self.mime_header['POT-Creation-Date'] = msgctl.mime_header['POT-Creation-Date']

        return (added_msgids, removed_msgids)

    def overwrite_context(self, msgctl):
        """For each message in the given message catalog that I know of,
        I will overwrite my contextual information with the given catalog's
        one."""
        for key in msgctl.keys():
            if self.has_key(key):
                self[key].references = msgctl[key].references
                for ac in msgctl[key].automatic_comments:
                    if ac not in self[key].automatic_comments:
                        self[key].automatic_comments.append(ac)

    def accept_ids(self, ids):
        """Remove all messages from the catalog where the id is not in argument
        'ids' (a list). Values are not touched. Returns the ids that were deleted.
        """
        removed_ids = []
        for key in self.keys():
            if key not in ids:
                del self[key]
                removed_ids.append(key)
        return removed_ids

    def accept_fct(self, fct):
        """Remove all messages from the catalog where fct return False for
        fct(msgid, msgstr). Returns the ids that were deleted.
        """
        removed_ids = []
        for key in self.keys():
            if not fct(key, self[key].msgstr):
                del self[key]
                removed_ids.append(key)
        return removed_ids

    def _initialize_with(self, filename):
        file = open(filename)
        parser = POParser(file)
        parser.read()
        file.close()
        self.update(parser.msgdict)
        try:
            self.commentary_header = self[''].comments
            self._parse_mime_header(self[''].msgstr)
            del self['']
        except KeyError, e:
            print >> sys.stderr, "%s lacks MIME header." % filename

    def _parse_mime_header(self, msgstr):
        pairs = [line.split(':', 1) for line in msgstr.split(r'\n') if line]
        for key, value in pairs:
            self.mime_header[key.strip()] = value.strip()
            if key.lower() == 'domain':
                self.domain = value.strip()

class POParser:
    """Parses an existing po- file and builds a dictionary according to
    MessageCatalog. POParser is the deserializer, POWriter the serializer.
    """

    def __init__(self, file):
        self._file = file
        self._in_paren = re.compile(r'"(.*)"')
        self.msgdict = odict() # see MessageCatalog for structure
        self.line = ''
        self.sameMessageEntry = True
        self.msgid = ''
        self.msgstr = ''
        self.references = []
        self.automatic_comments = []
        self.comments = []

    def read(self):
        """Start reading from file.

        After the call to read() has finished, you may access the structure
        that I read in through the ``msgdict`` attribute."""

        for no, line in enumerate(self._file):
            self.line = line

            oldstatus = self.sameMessageEntry
            if oldstatus:
                self._readSameMessage()
            else:
                self._readNewMessage()
            
            newstatus = self.sameMessageEntry
            if oldstatus != newstatus:
                # function changed stateid: call new function with same line
                if newstatus:
                    self._readSameMessage()
                else:
                    self._readNewMessage()

        # last msg
        if not self.msgdict.has_key(self.msgid):
            self.line = '#:'
            self._readNewMessage()

    def _readSameMessage(self):
        """We're reading a comment or msgid."""
        line = self.line
        if line.startswith('msgstr'):
            self.sameMessageEntry = False
        elif line.startswith('#:'):
            self.references.append(line[2:].strip())
        elif line.startswith('#.'):
            line = line[2:].strip()
            ls = line.startswith
            if ls(ORIGINAL_COMMENT):
                line = line.replace(ORIGINAL_COMMENT, DEFAULT_COMMENT)
            if not line in self.automatic_comments:
                self.automatic_comments.append(line)
        elif line.startswith('#'):
            line = line[1:].strip()
            ls = line.startswith
            if ls(ORIGINAL_COMMENT) or ls(DEFAULT_COMMENT):
                line = line.replace(ORIGINAL_COMMENT, DEFAULT_COMMENT)
                if not line in self.automatic_comments:
                    self.automatic_comments.append(line)
            else:
                self.comments.append(line)
        else:
            search = self._in_paren.search(line)
            if search:
                self.msgid += search.groups()[0]

    def _readNewMessage(self):
        """We're reading msgstr."""
        sw = self.line.startswith
        if sw('#') or sw('msgid'):
            self.sameMessageEntry = True
            self.msgdict[self.msgid] = MessageEntry(self.msgid,\
                                               msgstr=self.msgstr,\
                                               references=self.references,\
                                               automatic_comments=self.automatic_comments,\
                                               comments=self.comments)
            # reset variables
            self.msgid = self.msgstr = ''
            self.references = []
            self.automatic_comments = []
            self.comments = []
        else:
            search = self._in_paren.search(self.line)
            if search:
                self.msgstr += search.groups()[0]

class POWriter:

    def __init__(self, file, catalog):
        """Initialize a POWriter with a filelike object that I am to write to."""
        self._file = file
        self._msgctl = catalog

    def _encode(self, line, input_encoding=None, output_encoding=None):
        """encode a given unicode type or string type to string type in encoding output_encoding"""
        content_type = self._msgctl.mime_header.get('Content-Type', 'text/plain; charset=utf-8')
        charset = content_type.split('=')
        encoding = charset[-1]

        # check if input is not type unicode
        if not isinstance(line, unicode):
            if input_encoding is None:
                # get input encoding from message catalog
                input_encoding = encoding
            line = unicode(line, input_encoding)
        
        if output_encoding is None:
            # get output encoding from message catalog
            output_encoding = encoding
        
        return line.encode(output_encoding)

    def _printToFile(self, file, string):
        """ Print wrapper which allows to specifiy an output encoding"""
        if not string:
            print >> file
        else:
            print >> file, self._encode(string)

    def write(self, sort=True, msgstrToComment=False, sync=False):
        """Start writing to file."""
        self._write_header()
        self._write_messages(sort=sort, msgstrToComment=msgstrToComment, sync=sync)

    def _write_header(self):
        """Writes out commentary and mime headers."""
        ctl = self._msgctl
        f = self._file

        # header
        for line in ctl.commentary_header:
            self._printToFile(f, '# %s' % line)

        if not ctl.mime_header: # mime-header n/a
            self._printToFile(f, False)
            return

        #write out mime:
        self._printToFile(f, 'msgid ""')
        self._printToFile(f, 'msgstr ""')

        for key in ctl.mime_header.keys():
            self._printToFile(f, '"%s: %s\\n"' % (key, ctl.mime_header[key]))

    def _write_messages(self, sort, msgstrToComment, sync):
        """Writes the messages out."""
        f = self._file
        ids = self._msgctl.keys()
        ids.sort()

        for id in ids:
            entry = self._msgctl[id]
            self._print_entry(f, id, entry, msgstrToComment=msgstrToComment, sync=sync)

        # File should end with a blank line
        self._printToFile(f,False)

    def _print_entry(self, f, id, entry, msgstrToComment, sync):
        """Writes a MessageEntry to file."""
        self._printToFile(f,False)

        msgstr = entry.msgstr
        comments = entry.comments
        automatic_comments = entry.automatic_comments

        msg_changed = False
        fuzzy = False

        for comment in comments:
            if not comment.startswith(', fuzzy') and not comment.startswith(' , fuzzy'):
                if comment.startswith('#'):
                    self._printToFile(f, '#%s' % comment)
                else:
                    self._printToFile(f, '# %s' % comment)
            else:
                fuzzy = True

        # used in pot methods
        if msgstrToComment and msgstr:
            # no html markup in the default comments as these are not
            # allowed in msgstr's either
            msgstr = msgstr.replace('"','\\\"')
            msgstr = msgstr.replace('&quot;','\\\"')
            msgstr = msgstr.replace('&amp;','&')
            msgstr = msgstr.replace('&hellip;','...')
            msgstr = msgstr.replace('&mdash;','-')
            self._printToFile(f, '#. %s"%s"' % (DEFAULT_COMMENT, msgstr))
            msgstr = ''

        # used in sync to filter duplicate default comments
        if sync:
            default_comments = [o for o in automatic_comments if o.startswith(DEFAULT_COMMENT)]
            if len(default_comments) > 1:
                msg_changed = True
                # the first element is the old comment, the second the new one
                automatic_comments.remove(default_comments[0])

        for ac in automatic_comments:
            self._printToFile(f, '#. %s' % ac)

        no = 0
        for ref in entry.references:
            if not '//' in ref:
                self._printToFile(f, '#: %s' % ref)
            else:
                refs = ref.split('//')
                if refs[0]:
                    self._printToFile(f, '#: %s//' % refs[0])
                if refs[1]:
                    self._printToFile(f, '#: %s' % refs[1].lstrip())
            no += 1
            if no >= MAX_OCCUR: break

        if msgstr and (msg_changed or fuzzy):
            self._printToFile(f, '#, fuzzy')

        self._printToFile(f, 'msgid "%s"' % id)
        if not '\\n' in msgstr:
            self._printToFile(f, 'msgstr "%s"' % msgstr)
        else:
            self._printToFile(f, 'msgstr ""')
            lines = msgstr.split('\\n')
            for line in lines[:-1]:
                self._printToFile(f, '"%s\\n"' % line)
            if lines[-1]:
                self._printToFile(f, '"%s"' % lines[-1])


class PTReader:
    """Reads in a list of page templates"""

    def __init__(self, path, domain='none'):

        self.domain = domain
        self.catalogs = {} # keyed by domain name
        self.path = path

    def read(self):
        """Reads in from all given ZPTs and builds up MessageCatalogs accordingly.

        The MessageCatalogs can after this call be accessed through attribute
        ``catalogs``, which indexes the MessageCatalogs by their domain.
        """
        from extract import tal_strings
        tal = tal_strings(self.path, domain=self.domain, exclude=('tests', 'docs'))

        for msgid in tal:

            msgstr = msgid or ''
            if isinstance(msgid, Message):
                msgstr = msgid.default or ''

            lines = msgstr.split("\n")
            for i in range(len(lines)):
                lines[i] = lines[i].strip()
                if lines[i]:
                    lines[i] = ' ' + lines[i]
            msgstr = ''.join(lines).strip()
                        
            if msgid and msgid <> '${DYNAMIC_CONTENT}':
                self._add_msg(msgid,
                              msgstr,
                              [],
                              [tal[msgid][0][0]+':'+str(tal[msgid][0][1])],
                              [],
                              self.domain)

        return []

    def _add_msg(self, msgid, msgstr, comments, filename, automatic_comments, domain):
        if not domain:
            print >> sys.stderr, 'No domain name for msgid "%s" in %s\n' % \
                  (msgid, filename)
            return

        if not self.catalogs.has_key(domain):
            self.catalogs[domain] = MessageCatalog(domain=domain)

        # check if the msgid is already in the catalog with a different text
        catalog = self.catalogs[domain]
        adding = True
        if catalog.has_key(msgid):
            cat_msgstr = catalog[msgid].msgstr
            if msgstr != cat_msgstr:
                print >> sys.stderr, "Error: msgid '%s' in %s already exists " \
                         "with a different msgstr (bad: %s, should be: %s)\n" \
                         "The references for the existent value are: %s\n" % \
                         (msgid, filename, msgstr, cat_msgstr, ''.join(catalog[msgid].references))
                adding = False

        if adding:
            self.catalogs[domain].add(msgid, msgstr=msgstr, comments=comments, references=filename, automatic_comments=automatic_comments)


class PYReader:
    """Reads in a list of python scripts"""

    def __init__(self, path, domain):

        self.domain = domain
        self.catalogs = {} # keyed by domain name
        self.path = path

    def read(self):
        """Reads in from all given PYs and builds up MessageCatalogs
        accordingly.

        The MessageCatalogs can after this call be accessed through attribute
        ``catalogs``, which indexes the MessageCatalogs by their domain.

        read returns the list of tuples (filename, errormsg), where filename
        is the name of the file that could not be read and errormsg a human
        readable error message.
        """

        include_default_domain = False
        python_only = True

        from extract import py_strings
        py = py_strings(self.path, self.domain, exclude=('tests', ))

        for msgid in py:
            self._add_msg(msgid,
                          msgid.default or '',
                          [],
                          [py[msgid][0][0]+':'+str(py[msgid][0][1])],
                          [],
                          self.domain)
        return []

    def _add_msg(self, msgid, msgstr, comments, references, automatic_comments, domain):
        if not domain:
            print >> sys.stderr, 'No domain name for msgid "%s" in %s\n' % \
                  (msgid, references)
            return

        if not self.catalogs.has_key(domain):
            self.catalogs[domain] = MessageCatalog(domain=domain)

        self.catalogs[domain].add(msgid, msgstr=msgstr, comments=comments, references=references, automatic_comments=automatic_comments)
