# -*- coding: utf-8 -*-
from i18ndude.utils import quote
from i18ndude.utils import wrapAndQuoteString
from i18ndude.utils import wrapString
from ordereddict import OrderedDict
from zope.i18nmessageid import Message
import os
import re
import sys
import time

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

MAX_OCCUR = 3  # maximum number of occurrences listed
# Set it to None to list all occurences


ORIGINAL_COMMENT = 'Original: '
DEFAULT_COMMENT = 'Default: '


def now():
    fmt = '%Y-%m-%d %H:%M+0000'
    return time.strftime(fmt, time.gmtime())


def is_literal_id(msgid):
    if '_' in msgid and ' ' not in msgid:
        return False
    else:
        return True


class MessageEntry:
    """ MessageEntry is class representing one msgid with its accompanying
    msgstr and optional positional information and comments.
    """

    def __init__(
            self, msgid, msgstr='',
            references=[], automatic_comments=[], comments=[]):
        """Build a MessageEntry.
        """
        self.msgid = msgid
        self.msgstr = msgstr
        self.references = references
        self.automatic_comments = automatic_comments
        self.comments = comments

    def __repr__(self):
        """Textual representation of a MessageEntry.
        """
        return ', '.join([
            self.msgid,
            self.msgstr,
            repr(self.references),
            repr(self.automatic_comments),
            repr(self.comments)
        ])

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
            default = comment.replace(DEFAULT_COMMENT + '\"', '')
            return default[:-1]
        return None

    def getDefaults(self):
        """Returns the text of the default comments"""
        comments = self.getDefaultComment(multiple=True)
        defaults = []
        if comments is None:
            return None
        for dc in comments:
            default = dc.replace(DEFAULT_COMMENT + '\"', '')
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
            orig = comment.replace(ORIGINAL_COMMENT + '\"', '')
            return orig[:-1]
        return None


class MessageCatalog(OrderedDict):
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
        OrderedDict.__init__(self, None)

        # XOR
        assert not (filename and domain)
        assert filename or domain

        self.commentary_header = DEFAULT_PO_HEADER
        self.mime_header = OrderedDict()
        for key, value in DEFAULT_PO_MIME:
            self.mime_header[key] = value

        self.filename = filename
        self.domain = domain
        self.encoding = 'utf-8'

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

    def update(self, dict=None):
        if dict is None:
            return
        for (key, val) in dict.items():
            if getattr(val, 'msgid', None) is not None:
                val.msgid = val.msgid.decode(self.encoding)
            if getattr(val, 'msgstr', None) is not None:
                val.msgstr = val.msgstr.decode(self.encoding)
            self[key.decode(self.encoding)] = val

    def add(self, msgid, msgstr='',
            comments=[], references=[], automatic_comments=[]):
        """Add an entry to the catalog.

        If the msgid already exists in the catalog, we only add comments,
        references and automatic comments to the entry."""
        if isinstance(msgid, MessageEntry):
            msgstr = msgid.msgstr
            references = msgid.references
            automatic_comments = msgid.automatic_comments
            comments = msgid.comments
            msgid = msgid.msgid
        if not isinstance(msgid, unicode):
            msgid = msgid.decode(self.encoding)
        if not isinstance(msgstr, unicode):
            msgstr = msgstr.decode(self.encoding)
        if msgid not in self:
            self[msgid] = MessageEntry(msgid, msgstr=msgstr, comments=comments,
                                       references=references,
                                       automatic_comments=automatic_comments)
        else:
            # We can have a msgid with an associated default in a page
            # template, and the same msgid with a different default in a Python
            # file
            if msgstr != self[msgid].msgstr:
                msg = u"Warning: msgid '%s' in %s already exists " \
                      u"with a different default (bad: %s, should be: %s)\n" \
                      u"The references for the existent value are:\n%s\n"
                msg = msg % (msgid,
                             u'\n'.join(references),
                             msgstr,
                             self[msgid].msgstr,
                             u'\n'.join(self[msgid].references))
                print >> sys.stderr, msg.encode('utf-8')
            if comments:
                comments = [
                    c for c in comments if c not in self[msgid].comments]
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

        Returns the ids that were added."""
        ids = []
        for key in msgctl:
            if key not in self:
                entry = msgctl[key]
                msgstr = defaultmsgstr or entry.msgstr
                if isinstance(key, Message):
                    msgstr = key.default or msgstr
                self.add(key, msgstr=msgstr, comments=entry.comments,
                         references=entry.references,
                         automatic_comments=entry.automatic_comments)
                ids.append(key)
            elif mergewarn:
                print >> sys.stderr,\
                    'Merge-Warning: Key is already in target-catalog: %s'\
                    % key.encode('utf-8')

        return ids

    def merge(self, msgctl):
        """Each msgid that I miss and ``msgctl`` contains will be included in
        my catalog."""
        for key in msgctl:
            entry = msgctl[key]
            self.add(key, msgstr=entry.msgstr, comments=entry.comments,
                     references=entry.references,
                     automatic_comments=entry.automatic_comments)

    def sync(self, msgctl):
        """Syncronize the catalog with the given one. This removes all messages
        which are not found anymore in the new catalog, adds additional ones
        and overwrites the comments with the ones from the given catalog. This
        is used in the sync command.
        """
        removed_msgids = [quote(msgid)
                          for msgid in self.accept_ids(msgctl.keys())]
        self.overwrite_context(msgctl)
        added_msgids = [quote(msgid)
                        for msgid in self.add_missing(msgctl)]

        self.mime_header[
            'POT-Creation-Date'] = msgctl.mime_header['POT-Creation-Date']

        return (added_msgids, removed_msgids)

    def overwrite_context(self, msgctl):
        """For each message in the given message catalog that I know of,
        I will overwrite my contextual information with the given catalog's
        one."""
        for key in msgctl.keys():
            if key in self:
                self[key].references = msgctl[key].references
                for ac in msgctl[key].automatic_comments:
                    if ac not in self[key].automatic_comments:
                        self[key].automatic_comments.append(ac)

    def accept_ids(self, ids):
        """Remove all messages from the catalog where the id is not in argument
        'ids' (a list). Values are not touched. Returns the ids that were
        deleted.
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
        header = parser.msgdict.get('')
        if header is None:
            print >> sys.stderr, (
                "%s misses 'msgid \"\"' and 'msgstr \"\"' "
                "near the top. Will be fixed." % filename)
        else:
            try:
                self.commentary_header = header.comments
                self._parse_mime_header(header.msgstr)
                del parser.msgdict['']
            except KeyError:
                print >> sys.stderr, "%s lacks MIME header." % filename
        # Update the file after the header has been read.
        self.update(parser.msgdict)

    def _parse_mime_header(self, msgstr):
        pairs = [line.split(':', 1) for line in msgstr.split(r'\n') if line]
        for key, value in pairs:
            self.mime_header[key.strip()] = value.strip()
            if key.lower() == 'domain':
                self.domain = value.strip()
            if key.lower() == 'content-type':
                self.encoding = value.strip().lower().split('=')[-1]


class POParser:

    """Parses an existing po- file and builds a dictionary according to
    MessageCatalog. POParser is the deserializer, POWriter the serializer.
    """

    def __init__(self, file):
        self._file = file
        self._in_paren = re.compile(r'"(.*)"')
        self.msgdict = OrderedDict()  # see MessageCatalog for structure
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
        if self.msgid not in self.msgdict:
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
            if line not in self.automatic_comments:
                self.automatic_comments.append(line)
        elif line.startswith('#'):
            line = line[1:].strip()
            ls = line.startswith
            if ls(ORIGINAL_COMMENT) or ls(DEFAULT_COMMENT):
                line = line.replace(ORIGINAL_COMMENT, DEFAULT_COMMENT)
                if line not in self.automatic_comments:
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
            self.msgdict[self.msgid] = MessageEntry(
                self.msgid, msgstr=self.msgstr, references=self.references,
                automatic_comments=self.automatic_comments,
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
        """Initialize a POWriter with a filelike object that I am to write to.
        """
        self._file = file
        self._msgctl = catalog

    def _encode(self, line, input_encoding=None, output_encoding=None):
        """encode a given unicode type or string type to string type
        in encoding output_encoding
        """
        content_type = self._msgctl.mime_header.get(
            'Content-Type', 'text/plain; charset=utf-8')
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
            return
        string = string.strip()
        print >> file, self._encode(string)

    def write(self, sort=True, msgstrToComment=False, sync=False):
        """Start writing to file."""
        self._write_header()
        self._write_messages(
            sort=sort, msgstrToComment=msgstrToComment, sync=sync)

    def _write_header(self):
        """Writes out commentary and mime headers."""
        ctl = self._msgctl
        f = self._file

        # header
        for line in ctl.commentary_header:
            self._printToFile(f, '# %s' % line)

        if not ctl.mime_header:  # mime-header n/a
            self._printToFile(f, False)
            return

        # write out mime:
        self._printToFile(f, 'msgid ""')
        self._printToFile(f, 'msgstr ""')

        for key in ctl.mime_header.keys():
            self._printToFile(f, '"%s: %s\\n"' % (key, ctl.mime_header[key]))

    def _write_messages(self, sort, msgstrToComment, sync):
        """Writes the messages out."""
        f = self._file
        ids = sorted(self._msgctl.keys())

        for id in ids:
            entry = self._msgctl[id]
            self._print_entry(
                f, id, entry, msgstrToComment=msgstrToComment, sync=sync)

    def _create_msgid(self, value):
        # Wrap over multiple lines if needed.
        values = wrapString(value)
        # Quote all lines and separate them by newlines.
        return 'msgid "%s"' % '"\n"'.join(values)

    def _create_msgstr(self, value):
        # Wrap over multiple lines if needed.
        values = wrapString(value)
        # Quote all lines and separate them by newlines.
        return 'msgstr "%s"' % '"\n"'.join(values)

    def _print_entry(self, f, id, entry, msgstrToComment, sync):
        """Writes a MessageEntry to file."""
        self._printToFile(f, False)

        msgstr = entry.msgstr
        comments = entry.comments
        automatic_comments = entry.automatic_comments

        msg_changed = False
        fuzzy = False

        for comment in comments:
            if not comment.startswith(', fuzzy')\
                    and not comment.startswith(' , fuzzy'):
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
            msgstr = msgstr.replace('"', '\\\"')
            msgstr = msgstr.replace('\n', '\\n')
            msgstr = msgstr.replace('&quot;', '\\\"')
            msgstr = msgstr.replace('&#xa0;', ' ')
            msgstr = msgstr.replace('&amp;', '&')
            msgstr = msgstr.replace('&hellip;', u'\u2026')
            msgstr = msgstr.replace('&#8230;', u'\u2026')
            msgstr = msgstr.replace('&mdash;', u'\u2014')
            msgstr = msgstr.replace('&#9632;', u'\u25A0')
            msgstr = msgstr.replace('&#9675;', u'\u25CB')
            msgstr = msgstr.replace('&#9679;', u'\u25CF')
            self._printToFile(f, '#. %s"%s"' % (DEFAULT_COMMENT, msgstr))
            msgstr = ''

        # used in sync to filter duplicate default comments
        if sync:
            default_comments = [
                o for o in automatic_comments if o.startswith(DEFAULT_COMMENT)]
            if len(default_comments) > 1:
                msg_changed = True
                # the first element is the old comment, the second the new one
                automatic_comments.remove(default_comments[0])

        for ac in automatic_comments:
            self._printToFile(f, '#. %s' % ac)

        # key is the filename, value is the filename or filename:lineno
        refs = {}
        for ref in entry.references:
            pparts = ref.split('Products%s' % os.sep)
            p2parts = ref.split('products%s' % os.sep)
            sparts = ref.split('src%s' % os.sep, 1)
            if len(pparts) > 1:
                ref = pparts[1]
            elif len(p2parts) > 1:
                ref = p2parts[1]
            elif len(sparts) > 1:
                ref = sparts[1]
            # Normalize path separators to unix-style
            ref.replace(os.sep, '/')

            # We can have two references to the same file
            # but with different line number. We only include
            # the reference once.
            filename = ref.split(':')[0]
            if filename not in refs:
                refs[filename] = ref

        # Support for max number of references
        refs_values = sorted(refs.values())
#        include_ellipsis = MAX_OCCUR is not None and \
#                           len(refs_values[MAX_OCCUR:])
        for idx, ref in enumerate(refs_values[:MAX_OCCUR]):
            self._printToFile(f, '#: %s' % ref)
#            if include_ellipsis and idx == MAX_OCCUR - 1:
# self._printToFile(f, '#: %s' % ref)
# self._printToFile(f, '#: ...')

        if msgstr and (msg_changed or fuzzy):
            self._printToFile(f, '#, fuzzy')

        # Add backslash escape to id.
        if '"' in id and u'\\"' not in id:
            id = id.replace('"', '\\"')

        self._printToFile(f, self._create_msgid(id))
        if '\\n' not in msgstr:
            self._printToFile(f, self._create_msgstr(msgstr))
        else:
            self._printToFile(f, 'msgstr ""')
            lines = msgstr.split('\\n')
            for line in lines[:-1]:
                # Restore the literal backslash-n at the end
                line += '\\n'
                # Wrap over multiple lines if needed.
                newline = wrapAndQuoteString(line)
                self._printToFile(f, newline)
            if lines[-1]:
                # This is the part after the last literal backslash-n
                newline = wrapAndQuoteString(lines[-1])
                self._printToFile(f, newline)


class PTReader:
    """Reads in a list of page templates.
    """

    def __init__(self, path, domain='none', exclude=()):

        self.domain = domain
        self.catalogs = {}  # keyed by domain name
        self.path = path
        self.exclude = exclude

    def read(self):
        """Reads in from all given ZPTs and builds up MessageCatalogs accordingly.

        The MessageCatalogs can after this call be accessed through attribute
        ``catalogs``, which indexes the MessageCatalogs by their domain.
        """
        from extract import tal_strings
        tal = tal_strings(self.path, domain=self.domain,
                          exclude=self.exclude + ('tests', 'docs'))

        for msgid in tal:

            msgstr = msgid.default or ''

            if msgid and msgid != '${DYNAMIC_CONTENT}':
                self._add_msg(msgid,
                              msgstr,
                              [],
                              [l[0] + ':' + str(l[1]) for l in tal[msgid]],
                              [],
                              self.domain)

        return []

    def _add_msg(self, msgid, msgstr, comments, filename, automatic_comments,
                 domain):
        if not domain:
            print >> sys.stderr, 'No domain name for msgid "%s" in %s\n' % \
                (msgid, filename)
            return

        if domain not in self.catalogs:
            self.catalogs[domain] = MessageCatalog(domain=domain)

        self.catalogs[domain].add(msgid, msgstr=msgstr, comments=comments,
                                  references=filename,
                                  automatic_comments=automatic_comments)


class PYReader:
    """Reads in a list of python scripts.
    """

    def __init__(self, path, domain, exclude=()):

        self.domain = domain
        self.catalogs = {}  # keyed by domain name
        self.path = path
        self.exclude = exclude

    def read(self):
        """Reads in from all given PYs and builds up MessageCatalogs
        accordingly.

        The MessageCatalogs can after this call be accessed through attribute
        ``catalogs``, which indexes the MessageCatalogs by their domain.

        read returns the list of tuples (filename, errormsg), where filename
        is the name of the file that could not be read and errormsg a human
        readable error message.
        """

        from extract import py_strings
        py = py_strings(self.path, self.domain,
                        exclude=self.exclude + ('tests', ))

        for msgid in py:
            self._add_msg(msgid,
                          msgid.default or '',
                          [],
                          [l[0] + ':' + str(l[1]) for l in py[msgid]],
                          [],
                          self.domain)
        return []

    def _add_msg(self, msgid, msgstr, comments, references, automatic_comments,
                 domain):
        if not domain:
            print >> sys.stderr, 'No domain name for msgid "%s" in %s\n' % \
                (msgid, references)
            return

        if domain not in self.catalogs:
            self.catalogs[domain] = MessageCatalog(domain=domain)

        self.catalogs[domain].add(msgid, msgstr=msgstr, comments=comments,
                                  references=references,
                                  automatic_comments=automatic_comments)


class GSReader(object):
    """Reads in a list of GenericSetup profile files.
    """

    def __init__(self, path, domain, exclude=()):
        self.domain = domain
        self.catalogs = {}  # keyed by domain name
        self.path = path
        self.exclude = exclude

    def read(self):
        """Reads in from all given xml's and builds up MessageCatalogs
        accordingly.

        The MessageCatalogs can after this call be accessed through attribute
        ``catalogs``, which indexes the MessageCatalogs by their domain.

        read returns the list of tuples (filename, errormsg), where filename
        is the name of the file that could not be read and errormsg a human
        readable error message.
        """

        from gsextract import gs_strings
        gs = gs_strings(self.path, self.domain,
                        exclude=self.exclude + ('tests', ))

        for domain in gs:
            for msgid in gs[domain]:
                self._add_msg(msgid[0],
                              msgid[1],
                              [],
                              [msgid[2]],
                              [],
                              domain)
        return []

    def _add_msg(self, msgid, msgstr, comments, references, automatic_comments,
                 domain):
        if not domain:
            print >> sys.stderr, 'No domain name for msgid "%s" in %s\n' % \
                (msgid, references)
            return

        if domain not in self.catalogs:
            self.catalogs[domain] = MessageCatalog(domain=domain)

        self.catalogs[domain].add(msgid, msgstr=msgstr, comments=comments,
                                  references=references,
                                  automatic_comments=automatic_comments)


class ZCMLReader(object):
    """Reads in a list of ZCML files.
    """

    def __init__(self, path, domain, exclude=()):
        self.domain = domain
        self.catalogs = {}  # keyed by domain name
        self.path = path
        self.exclude = exclude

    def read(self):
        """Reads in from all given zcml's and builds up MessageCatalogs
        accordingly.

        The MessageCatalogs can after this call be accessed through attribute
        ``catalogs``, which indexes the MessageCatalogs by their domain.

        read returns the list of tuples (filename, errormsg), where filename
        is the name of the file that could not be read and errormsg a human
        readable error message.
        """

        from zcmlextract import zcml_strings
        zcml = zcml_strings(self.path, self.domain,
                            exclude=self.exclude + ('tests', ))

        for domain in zcml:
            for msgid in zcml[domain]:
                self._add_msg(msgid[0],
                              msgid[1],
                              [],
                              [msgid[2]],
                              [],
                              domain)
        return []

    def _add_msg(self, msgid, msgstr, comments, references, automatic_comments,
                 domain):
        if not domain:
            print >> sys.stderr, 'No domain name for msgid "%s" in %s\n' % \
                (msgid, references)
            return

        if domain not in self.catalogs:
            self.catalogs[domain] = MessageCatalog(domain=domain)

        self.catalogs[domain].add(msgid, msgstr=msgstr, comments=comments,
                                  references=references,
                                  automatic_comments=automatic_comments)
