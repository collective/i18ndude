import re, sys, copy, time
import xml.dom.minidom
import xml.sax

ELEMENT_NODE = xml.dom.Node.ELEMENT_NODE

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
        return '' + self.msgid + self.msgstr + repr(self.references) + repr(self.automatic_comments) + repr(self.comments)

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

    def getDefaultComment(self):
        """Returns the automatic comment starting with Default: """
        for c in self.automatic_comments:
            if c.startswith(DEFAULT_COMMENT):
                return c
        return None

    def getDefault(self):
        """Returns the text of the default comment"""
        comment = self.getDefaultComment()
        if comment is not None:
            default = comment.replace(DEFAULT_COMMENT+'\"','')
            return default[:-1]
        return None

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
    """MessageCatalog is a collection of msgids, their msgstrs and optional
    positional information.

    If we're reading in from a .po-file, MessageCatalog also contains an
    individual MIME-Header and a domain. While a default MIME-Header is
    available, a domain must always be supplied.

    MessageCatalog's dictionary maps msgids to information that is available
    for those. The values in this dictionary are in the form
    (msgstr, [occurrence, ...], [comment, ...]).

    An occurrence has the form (filename, context), where context is a list of
    strings that give the translator a contextual hint on how the msgid is used
    in the page templates. A comment is a string."""


    def __init__(self, filename=None, domain=None, allcomments=False):
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
            self._initialize_with(filename, allcomments=allcomments)
        elif domain:
            self.mime_header['Domain'] = domain

    def add(self, msgid, msgstr='', filename='', excerpt=[]):
        """Add a entry into the catalogue.

        If the msgid already exists in my catalog, I will only add filename
        and excerpt to the entry."""

        if not self.has_key(msgid):
            self[msgid] = (msgstr, [(filename, excerpt)], [])
        else:
            if filename and excerpt:
                occurrences = self[msgid][1]
                occurrences.append((filename, excerpt))

    def addToSameFileName(self, msgid, msgstr='', filename='', excerpt=[]):
        """Add a entry into the catalogue to an existing filename.

        I will only add excerpt to the entry.
        """
        assert filename

        if not self.has_key(msgid):
            self[msgid] = (msgstr, [(filename, excerpt)], [])
        else:
            if filename and excerpt:
                occurrences = self[msgid][1]
                for occur in occurrences:
                    if filename == occur[0]:
                        if not excerpt[0] in occur[1]:
                            occurrences = (filename, occur[1].extend(excerpt))

    def get_comment(self, msgid):
        """Returns the commentary lines that I have for msgid."""

        assert msgid in self
        return self[msgid][2][:]

    def get_original_comment(self, msgid):
        """Returns the commentary line starting with Original: that
        I have for msgid."""

        orig_comment = None
        assert msgid in self
        for comment in self[msgid][2][:]:
            if comment.startswith(ORIGINAL_COMMENT):
                orig_comment = comment

        return orig_comment

    def get_original(self, msgid):
        """Returns the original text for a msgid as found in the comment starting
        with Original: ."""

        assert msgid in self
        orig_comment = self.get_original_comment(msgid)
        if orig_comment is not None:
            orig = orig_comment.replace(ORIGINAL_COMMENT+'\"','')
            return orig[:-1]
        return None

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
                self[key] = (defaultmsgstr, entry[1][:], entry[2][:])
                ids.append(key)
            elif mergewarn:
                print >> sys.stderr, \
                    'Merge-Warning: Key is already in target-catalog: %s' % key

        return ids

    def overwrite_context(self, msgctl):
        """For each message in the given message catalog that I know of,
        I will overwrite my contextual information with the given catalog's
        one."""

        for key in msgctl.keys():
            if self.has_key(key):
                for comment in msgctl[key][2]:
                    if comment not in self[key][2]:
                        self[key][2].append(comment)

                self[key] = (self[key][0], msgctl[key][1], self[key][2])

    def accept_ids(self, ids):
        """Remove all messages from the catalog where the id is not in argument
        ``ids`` (a list).

        Values are not touched.

        Returns the ids that were deleted."""

        removed_ids = []
        for key in self.keys():
            if key not in ids:
                del self[key]
                removed_ids.append(key)

        return removed_ids

    def accept_fct(self, fct):
        """Remove all messages from the catalog where fct return False for
        fct(msgid, msgstr).

        Returns the ids that were deleted."""

        removed_ids = []
        for key in self.keys():
            if not fct(key, self[key][0]):
                del self[key]
                removed_ids.append(key)

        return removed_ids

    def _initialize_with(self, filename, allcomments=False):
        file = open(filename)
        parser = POParser(file)
        parser.read(allcomments=allcomments)
        file.close()
        self.update(parser.msgdict)
        try:
            self.commentary_header = self[''][2]
            self._parse_mime_header(self[''][0])
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
    MessageCatalog.

    POParser is the deserializer, POWriter the serializer.
    """

    def __init__(self, file):
        self._file = file
        self._in_paren = re.compile(r'"(.*)"')
        self.msgdict = odict() # see MessageCatalog for structure

    def read(self, allcomments=False):
        """Start reading from file.

        After the call to read() has finished, you may access the structure
        that I read in through the ``msgdict`` attribute."""

        state = {'stateid': 1,
                 'msgid': '',
                 'msgstr': '',
                 'occurrence': {}, # (filename, context)
                 'comment': [], # lines
                 'currfile': '',
                 'line': '',
                 'lineno': 0}

        for no, line in enumerate(self._file):
            state['line'] = line
            state['lineno'] = no + 1

            oldstate = state['stateid']
            fun = self._get_statefun(oldstate)
            fun(state, allcomments=allcomments)
            newstate = state['stateid']
            if oldstate != newstate:
                # function changed stateid: call new function with same line
                fun = self._get_statefun(newstate)
                fun(state, allcomments=allcomments)

        # last msg
        if not self.msgdict.has_key(state['msgid']):
            state['line'] = '#:' # _is_new_msg returns True for this
            self._do_state2(state)

    def _is_new_msg(self, line):
        sw = line.startswith
        if sw('#') or sw('msgid'): # a comment starts a new msg
            return True
        else:
            return False

    def _get_statefun(self, id):
        fun = getattr(self, '_do_state%s' % id, None)
        assert fun
        return fun

    def _do_state1(self, state, allcomments=False):
        """We're reading special comments (#: and #.) and msgid."""

        line = state['line']
        if line.startswith('msgstr'):
            state['stateid'] = 2 # change state

        elif line.startswith('#:'): # context: filename
            line = line.strip()
            currfile = line.split()[-1]
            state['currfile'] = currfile
            if currfile in state['occurrence']: return
            state['occurrence'][currfile] = []

        elif line.startswith('#.'): # context: excerpt
            occurrence, currfile = state['occurrence'], state['currfile']
            if not occurrence.has_key(currfile) or not currfile:
                pass
##                 print >> sys.stderr, \
##                       "Skipping contextual information at L%s in %s." % \
##                       (state['lineno'], self._file.name)

            else:
                if len(line) > 2 and line[2] == ' ': col = 3
                else: col = 2
                occurrence[currfile].append(line[col:].rstrip())

        elif line.startswith('#'):
            # this one isnt the solution, but better than having generated
            # lines "## 2 more: file1, file2, file3" generated several times.
            # Ignore those lines!
            if not line.startswith('##') or allcomments:
                state['comment'].append(line[1:].strip())

        else:
            search = self._in_paren.search(line)
            if search:
                state['msgid'] += search.groups()[0]
            else:
                pass
##                 print >> sys.stderr, \
##                       "Expected quotation marks at L%s in %s." % \
##                       (state['lineno'], self._file.name)

    def _do_state2(self, state, allcomments=False):
        """We're reading msgstr."""

        line = state['line']
        if self._is_new_msg(line): # one element was collected
            state['stateid'] = 1 # change state
            occurrences = [(fn, ctxt) for (fn, ctxt) in state['occurrence'].items()]
            entry = (state['msgstr'], occurrences, state['comment'])
            self.msgdict[state['msgid']] = entry

            # reset state variables
            state['msgid'] = state['msgstr'] = state['currfile'] = ''
            state['occurrence'].clear()
            state['comment'] = []

        elif line.startswith('#'):
            state['comment'].append(line[1:].strip())

        else:
            search = self._in_paren.search(line)
            if search:
                state['msgstr'] += search.groups()[0]


class POWriter:

    def __init__(self, file, catalog):
        """Initialize a POWriter.

        ``file`` is the filelike object that I am to write to.
        """

        self._file = file
        self._msgctl = catalog

    def _encode(self, line, input_encoding=None, output_encoding=None):
        # encode a give unicode type or string type to string type in encoding output_encoding

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

    def _print_entry(self, f, id, entry, msgstrToComment, sync):

        self._printToFile(f,False)

        msgstr = entry[0]
        occurrences = entry[1]
        comments = entry[2]

        no = 0
        known_ctxts = {}

        for filename, context in occurrences:
            known_key = ''.join([line.strip() for line in context])
            if known_key in known_ctxts:  # skip those with the same excerpt
                continue

            self._printToFile(f, '#: %s' % filename)
            for line in context:
                self._printToFile(f, '#. %s' % line.rstrip())

            known_ctxts[known_key] = True

            no += 1
            if no >= MAX_OCCUR: break

        # used in pot methods
        if msgstrToComment and msgstr:
            # no html markup in the original comments as these are not
            # allowed in msgstr's either
            msgstr = msgstr.replace('&quot;','\\\"')
            msgstr = msgstr.replace('&amp;','&')
            msgstr = msgstr.replace('&hellip;','...')
            self._printToFile(f, '# %s"%s"' % (ORIGINAL_COMMENT, msgstr))
            msgstr = ''

        msg_changed = False

        # used in sync to filter duplicate Original comments
        if sync:
            original_comments = [o for o in comments if o.startswith(ORIGINAL_COMMENT)]
            if len(original_comments) > 1:
                msg_changed = True
                # the first element is the old comment, the second the new one
                comments.remove(original_comments[0])

        for comment in comments:
            if not comment.startswith(', fuzzy') and not comment.startswith(' , fuzzy'):
                if comment.startswith('#'):
                    self._printToFile(f, '#%s' % comment)
                else:
                    self._printToFile(f, '# %s' % comment)

        fuzzy = len([c for c in comments if c.startswith(', fuzzy') or c.startswith(' , fuzzy')])
        if msg_changed or fuzzy>0:
            self._printToFile(f, '#, fuzzy')

        self._printToFile(f, 'msgid "%s"' % id)
        self._printToFile(f, 'msgstr "%s"' % msgstr)

        self._printToFile(f, False)


class PTReader:
    """Reads in a list of page templates"""
    def __init__(self, filenames):

        self.catalogs = {} # keyed by domain name
        self._filenames = filenames
        self._curr_doc = None

    def read(self):
        """Reads in from all given ZPTs and builds up MessageCatalogs
        accordingly.

        The MessageCatalogs can after this call be accessed through attribute
        ``catalogs``, which indexes the MessageCatalogs by their domain.

        read returns the list of tuples (filename, errormsg), where filename
        is the name of the file that could not be read and errormsg a human
        readable error message.
        """

        troubles = []
        for fn in self._filenames:
            try:
                content = common.prepare_xml(open(fn))
                doc = xml.dom.minidom.parse(content)
            except Exception, e: # exceptions may be sax-parser specific :(
                troubles.append((fn, str(e)))
            else:
                self._curr_doc = doc
                self._curr_fn = fn
                self._do_element(doc.documentElement, domain=None)

        return troubles

    def _do_element(self, element, domain):
        domain = element.getAttribute('i18n:domain') or domain

        if element.hasAttribute('i18n:translate'):
            self._do_translate(element, domain)
        if element.hasAttribute('i18n:attributes'):
            self._do_attributes(element, domain)

        for child in element.childNodes:
            if child.nodeType == ELEMENT_NODE:
                self._do_element(child, domain)

    def _do_translate(self, element, domain):
        filename = self._curr_fn
        excerpt = self._make_excerpt(element)
        msgid = element.getAttribute('i18n:translate')

        if msgid == '':
            if element.hasAttribute('tal:content') or \
               element.hasAttribute('tal:replace') or \
               element.hasAttribute('content') or \
               element.hasAttribute('replace'):
                print >> sys.stderr, 'Assuming rendered msgid in %s, not included:\n  %s\n' % \
                      (self._curr_fn, element.toprettyxml('  ', '\n  '))
            else:
                # tuttle@bbs.cvut.cz, XXX: XML quoting persists here, but
                # even \" is untranslatable here either. Better go with
                # non-literals in that case.
                msgid = self._make_msgstr(element)

                print >> sys.stderr, 'Warning: Literal msgids should be avoided in %s, still adding:\n  %s\n' % \
                      (self._curr_fn, element.toprettyxml('  ', '\n  '))

        if msgid:
            msgstr = self._make_msgstr(element)
            self._add_msg(msgid, msgstr, filename, excerpt, domain)


    def _do_attributes(self, element, domain):
        rendered = []
        if element.hasAttribute('tal:attributes'):
            attrs = element.getAttribute('tal:attributes').split(';')
            attrs = [attr.strip() for attr in attrs if attr.strip()]
            rendered = [attr.split()[0] for attr in attrs]

        filename = self._curr_fn
        excerpt = self._make_excerpt(element)
        excerpt = '\n'.join(excerpt)
        # XXX A reasonable way to find the end of the tag is needed here:
        gt = excerpt.find('>') + 1
        excerpt = excerpt[:gt].split('\n')
        
        i18nattrs = element.getAttribute('i18n:attributes');
        
        # construct list of (attrname, msgid) pairs
        if i18nattrs.find(';') == -1:	# old syntax without explicit msgids
            attrs = [(attrname, element.getAttribute(attrname), element.getAttribute(attrname))
                     for attrname in i18nattrs.split()]
        else:                           # new syntax with explicit msgids
            attrs = [(adata[0],
                      len(adata) > 1 and adata[1]  # explicit msgid given
                                      or element.getAttribute(adata[0]),
                                      element.getAttribute(adata[0]))
                     for adata in [attr.strip().split(None, 1)
                                   for attr in i18nattrs.split(';')]
                     if adata]

        for attrname, msgid, msgstr in attrs:
            if attrname in rendered:
                print >> sys.stderr, 'Assuming rendered msgid in %s, not included:\n%s\n' % \
                      (self._curr_fn, element.toprettyxml('  '))
                continue
            if msgid:
                self._add_msg(msgid, msgstr, filename, excerpt, domain)

    def _make_excerpt(self, element):
        prettynode = copy.deepcopy(element)
        self._make_pretty(prettynode)
        lines = prettynode.toprettyxml(' ').split('\n')
        lines = filter(lambda line: line.strip(), lines)
        return lines

    def _make_pretty(self, node):
        """Replace named subelements with ${name}."""
        for child in node.childNodes:
            if child.nodeType == ELEMENT_NODE:
                if child.hasAttribute('i18n:name'):
                    replacement = '${%s}' % child.getAttribute('i18n:name')
                    newchild = self._curr_doc.createTextNode(replacement)
                    node.replaceChild(newchild, child)
                else:
                    self._make_pretty(child)

    def _make_msgstr(self, element):
        node = copy.deepcopy(element)
        self._make_pretty(node)
        msgstr = ''
        for child in node.childNodes:
            chunk = child.toxml()
            # XXX Do we need to escape anything else?
            chunk = chunk.replace('"', '\\"')
            chunk = ' '.join(chunk.split()) + ' '
            if chunk != ' ':
                msgstr += chunk

        return msgstr.strip()

    def _add_msg(self, msgid, msgstr, filename, excerpt, domain):
        if not domain:
            print >> sys.stderr, 'No domain name for msgid "%s" in %s\n' % \
                  (msgid, filename)
            return

        if not self.catalogs.has_key(domain):
            self.catalogs[domain] = MessageCatalog(domain=domain)

        self.catalogs[domain].add(msgid, msgstr=msgstr,
                                  filename=filename, excerpt=excerpt)

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

        from pystrings import py_strings
        py = py_strings(self.path, self.domain)

        for msgid in py:
            self._add_msg(msgid, '', py[msgid][0][0], [], self.domain)

        return []

    def _add_msg(self, msgid, msgstr, filename, excerpt, domain):
        if not domain:
            print >> sys.stderr, 'No domain name for msgid "%s" in %s\n' % \
                  (msgid, filename)
            return

        if not self.catalogs.has_key(domain):
            self.catalogs[domain] = MessageCatalog(domain=domain)

        self.catalogs[domain].add(msgid, msgstr=msgstr,
                                  filename=filename, excerpt=excerpt)

