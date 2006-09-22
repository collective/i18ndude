#!/usr/bin/env python

"""Extract message strings from python modules
"""
import os, sys, fnmatch
import tokenize
from pygettext import safe_eval, make_escapes


class TokenEater(object):
    """This is based on pygettext.py with some ideas from extract.py.
    """
    def __init__(self):
        self.__messages = {}
        self.__state = self.__waiting
        self.__data = []
        self.__lineno = -1
        self.__freshmodule = 1
        self.__curfile = None

    def __call__(self, ttype, tstring, stup, etup, line):
        self.__state(ttype, tstring, stup[0])

    def __waiting(self, ttype, tstring, lineno):
        # Which functions to look for
        if ttype == tokenize.NAME and tstring in ['_','translate','utranslate']:
            self.__state = self.__keywordseen

    def __suiteseen(self, ttype, tstring, lineno):
        # ignore anything until we see the colon
        if ttype == tokenize.OP and tstring == ':':
            self.__state = self.__suitedocstring

    def __suitedocstring(self, ttype, tstring, lineno):

        # ignore any intervening noise
        if ttype == tokenize.STRING:
            self.__addentry(safe_eval(tstring), lineno, isdocstring=1)
            self.__state = self.__waiting
        elif ttype not in (tokenize.NEWLINE, tokenize.INDENT,
                           tokenize.COMMENT):
            # there was no class docstring
            self.__state = self.__waiting

    def __keywordseen(self, ttype, tstring, lineno):
        if ttype == tokenize.OP and tstring == '(':
            self.__data = []
            self.__msgid = ''
            self.__lineno = lineno
            self.__state = self.__openseen
        else:
            self.__state = self.__waiting

    def __openseen(self, ttype, tstring, lineno):
        if ttype == tokenize.OP and tstring == ')':
            if self.__data or self.__msgid:
                if self.__msgid:
                    msgid = self.__msgid
                    default = ''.join(self.__data)
                else:
                    msgid = ''.join(self.__data)
                    default = None
                self.__addentry(msgid, lineno, default=default)
            self.__state = self.__waiting
        elif ttype == tokenize.OP and tstring == ',':
            self.__msgid = ''.join(self.__data)
            self.__data = []
        elif ttype == tokenize.STRING:
            self.__data.append(safe_eval(tstring))
        # XXX Ignore most things or print out warning
        elif ttype == tokenize.OP and tstring in ['{',':','}','.','(',')','[',']','=','%']:
            self.__data = []
        elif ttype in [tokenize.NAME, tokenize.NUMBER] or tstring == '"':
            self.__data = []
        elif ttype not in [tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT,
                           tokenize.NEWLINE, tokenize.NL]:
            # warn if we see anything else than STRING or whitespace
            print >> sys.stderr, '* %(file)s:%(lineno)s: Seen unexpected token "%(typ)s %(token)s"' % {'token': tstring, 'typ': ttype, 'file': self.__curfile, 'lineno': self.__lineno}
            self.__state = self.__waiting

    def __addentry(self, msg, lineno=None, isdocstring=0, default=''):
        if lineno is None:
            lineno = self.__lineno

        entry = (self.__curfile, lineno)
        self.__messages.setdefault(msg, {})[entry] = default

    def set_filename(self, filename):
        self.__curfile = filename
        self.__freshmodule = 1

    def getCatalog(self):
        catalog = {}
        reverse = {}
        for k, v in self.__messages.items():
            keys = v.keys()
            keys.sort()
            reverse.setdefault(tuple(keys), []).append((k, v))
        rkeys = reverse.keys()
        rkeys.sort()
        for rkey in rkeys:
            rentries = reverse[rkey]
            rentries.sort()
            for msgid, locations in rentries:
                catalog[msgid] = []
                
                for key in locations:
                    filename, lineno = key
                    catalog[msgid].append((filename, lineno, locations[key]))
        return catalog

def find_files(dir, pattern, exclude=()):
    files = []

    def visit(files, dirname, names):
        files += [os.path.join(dirname, name)
                  for name in fnmatch.filter(names, pattern)
                  if name not in exclude]
        
    os.path.walk(dir, visit, files)
    return files

def py_strings(dir, domain="None"):
    """Retrieve all Python messages from dir that are in the domain.
    """
    eater = TokenEater()
    make_escapes(0)
    for filename in find_files(dir, '*.*py', 
                               exclude=('pygettext.py')):
        fp = open(filename)
        try:
            eater.set_filename(filename)
            try:
                tokenize.tokenize(fp.readline, eater)
            except tokenize.TokenError, e:
                print >> sys.stderr, '%s: %s, line %d, column %d' % (
                    e[0], filename, e[1][0], e[1][1])
        finally:
            fp.close()            
    return eater.getCatalog()

