#!python

#    Copyright (C) 2003-2007 Daniel Nouri <dpunktnpunkt@web.de>

#    If you find any bugs in here they were probably added by
#    Hanno Schlichting <plone@hannosch.info>

#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307, USA

# -----------------------------------------------------------------------------

"""Usage: i18ndude command [options] [path | file1 file2 ...]]

i18ndude performs various tasks related to ZPT's, Python Scripts and i18n.

Unless the -h, or --help option is given one of the commands below must be
present:

   find-untranslated [-s|-n] [file1 [file2 ...]]
          Provide a list of ZPT filenames and I will output a report of places
          where I suspect untranslated messages, i.e. tags for which
          "i18n:translate" or "i18n:attributes" are missing.

          If you provide the -s option, the report will only contain a summary
          of errors and warnings for each file (or no output if there are no
          errors or warnings). If you provide the -n option, the report will
          contain only the errors for each file.

   rebuild-pot --pot <filename> --create <domain> [--merge <filename>
   [--merge2 <filename>]] [--exclude="<ignore1> <ignore2> ..."] path [path2 ...]
          Given a pot-file via the --pot option you can specify one or more
          directories which including all sub-folders will be searched for
          PageTemplates (*.*pt) and Python scripts (*.*py).

          Make sure you have a backup copy of the original pot-file in case
          you need to fill back in ids by hand.

          If you give me an additional pot-file with the --merge <filename>
          option, I try to merge these msgids into the target-pot file
          afterwards. If a msgid already exists in the ones I found in the
          ZPTs, I'll warn you and ignore that msgid. I take the mime-header
          from this additional pot-file. If you provide a second pot-file via
          --merge2 <filename> I'll merge this into the first merge's result

          You can also provide a list of filenames which should not be included
          by using the --exclude argument, which takes a whitespace delimited
          list of files.

   merge --pot <filename> --merge <filename> [--merge2 <filename>]
          Given a pot-file via the --pot option and a second
          pot-file with the --merge <filename> option, I try to merge
          these msgids into the target-pot file. If a msgid already
          exists, I'll warn you and ignore that msgid.

          If you provide a --merge2 <filename> I'll first merge this one
          in addition to the first one.

   sync --pot <filename> file1 [file2 ...]
          Given a pot-file with the --pot option and a list of po-files I'll
          remove from the po files those message translations of which the
          msgids are not in the pot-file and add messages that the pot-file has
          but the po-file doesn't.

   filter <file1> <file2>
          Given two pot-files I will write a copy of file1 to stdout with all
          messages removed that are also in file2, i.e. where msgids match.

   admix <file1> <file2>
          Given two po-files I will look for translated entries in file2 that
          are untranslated in file1. I add these translations (msgstrs) to
          file1. Note that this will not affect the number of entries in file1.

   list --products <product1> [<product2> ...]
          This will create a simple listing that displays how much of the
          combined products pot's is translated for each language. Run this
          from the directory containing the pot-files.
"""

import os, sys
import getopt
import xml.sax

from i18ndude import common, untranslated, catalog, visualisation, utils

def usage(code, msg=''):
    print >> sys.stderr, __doc__
    if msg:
        print >> sys.stderr, msg
    sys.exit(code)

def short_usage(code, msg=''):
    if msg:
        print >> sys.stderr, msg
    print >> sys.stderr, u"Type i18ndude<Enter> to see the help."
    sys.exit(code)

def filter_isfile(files):
    result = []
    for name in files: # parse file by file
        name = name.strip()
        if os.path.isdir(name): # descend recursively
            join = lambda file: os.path.join(name, file)
            subdirs = filter_isfile([path for path in
                                     map(join, os.listdir(name))
                                     if os.path.isdir(path) or
                                     os.path.splitext(path)[1].endswith('pt')])
            result += subdirs

        elif not os.path.isfile(name):
            print >> sys.stderr, 'Warning: %s is not a file or is ignored.' % name

        else:
            result.append(name)
    return result

def find_untranslated():
    try:
        opts, files = getopt.getopt(sys.argv[2:], 'sn', ('silent','nosummary',))
    except getopt.GetoptError, e:
        usage(1)

    parser = xml.sax.make_parser(['expat'])
    # disable external validation to make it work without network access
    parser.setFeature(xml.sax.handler.feature_external_ges, False)
    parser.setFeature(xml.sax.handler.feature_external_pes, False)
    handler = untranslated.VerboseHandler(parser, sys.stdout) # default

    for opt, arg in opts:
        if opt in ('-s', '--silent'):
            handler = untranslated.SilentHandler(parser, sys.stdout)
        elif opt in ('-n', '--nosummary'):
            handler = untranslated.NoSummaryVerboseHandler(parser, sys.stdout)
        elif opt in ('-h', '--help'):
            usage(0)

    parser.setContentHandler(handler)

    for filename in filter_isfile(files): # parse file by file
        handler.set_filename(filename)
        content = common.prepare_xml(open(filename))

        try:
            parser.parse(content)
        except xml.sax.SAXException, e:
            handler.log('ERROR in document:\n%s' % e, 'FATAL')
        except KeyboardInterrupt:
            print >> sys.stderr, 'Interrupted by user.'
            sys.exit(0)
        except Exception, e:
            handler.log('ERROR in document:\n%s' % e, 'FATAL')


def rebuild_pot():
    try:
        opts, files = getopt.getopt(sys.argv[2:], 'mp:c:',
                                   ('pot=', 'create=', 'merge=', 'merge2=', 'exclude='))
    except:
        usage(1)

    pot_fn = None
    merge_fn = None
    merge2_fn = None
    create_domain = None
    exclude = ()
    for opt, arg in opts:
        if opt in ('-p', '--pot'):
            pot_fn = arg
        if opt in ('-c', '--create'):
            create_domain = arg
        if opt in ('-m', '--merge'):
            merge_fn = arg
        if opt in ('--merge2'):
            merge2_fn = arg
        if opt in ('--exclude'):
            exclude = tuple(arg.split())

    if not pot_fn:
        short_usage(1, u"No pot file specified as target with --pot.")

    if merge2_fn == merge_fn:
        merge2_fn = False

    path = files
    merge_ctl = None

    try:
        if create_domain is not None:
            orig_ctl = catalog.MessageCatalog(domain=create_domain)
        else:
            orig_ctl = catalog.MessageCatalog(filename=pot_fn)
        if merge_fn:
            merge_ctl = catalog.MessageCatalog(filename=merge_fn)
        if merge2_fn:
            merge2_ctl = catalog.MessageCatalog(filename=merge2_fn)
        ptreader = catalog.PTReader(path, create_domain, exclude=exclude)
        pyreader = catalog.PYReader(path, create_domain, exclude=exclude)
        gsreader = catalog.GSReader(path, create_domain, exclude=exclude)
    except IOError, e:
        short_usage(0, 'I/O Error: %s' % e)

    ptresult = ptreader.read()
    pyresult = pyreader.read()
    gsresult = gsreader.read()

    domain = orig_ctl.domain

    ptctl = pyctl = gsctl = {}
    if domain in ptreader.catalogs:
        ptctl = ptreader.catalogs[domain]
        comments = {} # keyed by msgid
        for key in orig_ctl.keys():
            if key in ptctl:
                # preserve comments
                ptctl[key].comments = ptctl[key].comments + orig_ctl.getComments(key)

    if domain in pyreader.catalogs:
        pyctl = pyreader.catalogs[domain]
        comments = {} # keyed by msgid
        for key in orig_ctl.keys():
            if key in pyctl:
                # preserve comments
                pyctl[key].comments = pyctl[key].comments + orig_ctl.getComments(key)

    if domain in gsreader.catalogs:
        gsctl = gsreader.catalogs[domain]
        # XXX Preserve comments?

    if not (ptctl or pyctl or gsctl):
        short_usage(0, 'No entries for domain "%s".' % domain)

    ctl = ptctl or pyctl or gsctl
    if pyctl and pyctl is not ctl:
        ctl.merge(pyctl)
    if gsctl and gsctl is not ctl:
        ctl.merge(gsctl)

    added_by_merge = []
    if merge_ctl is not None:
        # use headers from merge-catalog
        ctl.commentary_header = merge_ctl.commentary_header
        ctl.mime_header = merge_ctl.mime_header
        # merge
        added_by_merge = ctl.add_missing(merge_ctl, mergewarn=True)
    else:
        # use headers from orig-catalog
        ctl.commentary_header = orig_ctl.commentary_header
        ctl.mime_header = orig_ctl.mime_header

    added_by_merge2 = []
    if merge2_fn:
        added_by_merge2 = ctl.add_missing(merge2_ctl, mergewarn=True)

    ctl.mime_header['POT-Creation-Date'] = catalog.now()
    file = open(pot_fn, 'w')
    writer = catalog.POWriter(file, ctl)
    writer.write(msgstrToComment=True)

def merge():
    try:
        opts, files = getopt.getopt(sys.argv[2:], 'sm:p:',
                                   ('pot=', 'merge=', 'merge2='))
    except:
        usage(1)

    pot_fn = None
    merge_fn = None
    create_domain = None
    for opt, arg in opts:
        if opt in ('-p', '--pot'):
            pot_fn = arg
        if opt in ('-m', '--merge'):
            merge_fn = arg
        if opt in ('--merge2'):
            merge2_fn = arg

    if not pot_fn:
        short_usage(1, u"No pot file specified as target with --pot.")
    if not merge_fn:
        short_usage(1, u"No potfile specified as source with --merge.")

    try:
        orig_ctl = catalog.MessageCatalog(filename=pot_fn)
        merge_ctl = catalog.MessageCatalog(filename=merge_fn)
        if merge2_fn:
            merge2_ctl = catalog.MessageCatalog(filename=merge2_fn)
    except IOError, e:
        short_usage(0, 'I/O Error: %s' % e)

    # merge
    added_by_merge = orig_ctl.add_missing(merge_ctl, '', 1)
    if merge2_fn:
        added_by_merge2 = orig_ctl.add_missing(merge2_ctl, '', 1)
    orig_ctl.mime_header['POT-Creation-Date'] = catalog.now()
    file = open(pot_fn, 'w')
    writer = catalog.POWriter(file, orig_ctl)
    writer.write(msgstrToComment=True)

def sync():
    try:
        opts, files = getopt.getopt(sys.argv[2:], 'p:', ('pot='))
    except getopt.GetoptError, e:
        usage(1)

    pot_fn = None
    for opt, arg in opts:
        if opt in ('-p', '--pot'):
            pot_fn = arg

    if not pot_fn:
        short_usage(1, u"No pot file specified as target with --pot.")

    files = filter_isfile(files)

    try:
        pot_ctl = catalog.MessageCatalog(filename=pot_fn)
        po_ctls = [catalog.MessageCatalog(filename=fn) for fn in files]
    except IOError, e:
        short_usage(1, 'I/O Error: %s' % e)

    for po in po_ctls:
        added_msgids, removed_msgids = po.sync(pot_ctl)

        file = open(po.filename, 'w')
        writer = catalog.POWriter(file, po)
        writer.write(msgstrToComment=False, sync=True)

        print '%s: %s added, %s removed' % (po.filename,
                                            len(added_msgids),
                                            len(removed_msgids))
        file.close()

def filter():
    if len(sys.argv[2:]) != 2:
        usage(1)

    file1 = sys.argv[2]
    file2 = sys.argv[3]

    f1_ctl = catalog.MessageCatalog(filename=file1)
    f2_ctl = catalog.MessageCatalog(filename=file2)

    for msgid in f1_ctl.keys():
        if msgid in f2_ctl:
            del f1_ctl[msgid]

    writer = catalog.POWriter(sys.stdout, f1_ctl)
    writer.write(sort=False, msgstrToComment=True)

def admix():
    if len(sys.argv) != 4:
        usage(1)

    fn = sys.argv[2]
    base_ctl = catalog.MessageCatalog(filename=fn)

    fn = sys.argv[3]
    mixin_ctl = catalog.MessageCatalog(filename=fn)

    for msgid in mixin_ctl:
        mixin_msgstr = mixin_ctl[msgid].msgstr

        if mixin_msgstr and msgid in base_ctl and not base_ctl[msgid].msgstr:
            entry = base_ctl[msgid]
            entry.msgstr = mixin_ctl[msgid].msgstr
            base_ctl[msgid] = entry

    writer = catalog.POWriter(sys.stdout, base_ctl)
    writer.write(sort=False)

def list():
    try:
        opts, files = getopt.getopt(sys.argv[2:], 'tp:',
                                    ('products=', 'table='))
    except:
        usage(1)

    table = False
    products = []
    for opt, arg in opts:
        if opt in ('-p', '--products'):
            products.append(arg)
        if opt in ('-t', '--table'):
            table = True

    if not products:
        short_usage(1, u"No products specified with --products.")

    products.extend(files)

    # get all the files
    pos = {}
    pots = {}
    for product in products:
        if not pos.get(product, False):
            pos[product] = []
        pos[product].extend(utils.getPoFiles(product=product))
        if not pots.get(product, False):
            pots[product] = []
        pots[product].extend(utils.getPotFiles(product=product))

    # create catalogs of them
    pot_ctl = None
    for product in pots:
        for file in pots[product]:
            ctl = catalog.MessageCatalog(filename=file)
            if pot_ctl is None:
                pot_ctl = ctl
            else:
                pot_ctl.merge(ctl)

    if not pot_ctl:
        short_usage(1, 'Error: No pot files found.')

    po_ctls = {}
    for product in pos:
        for file in pos[product]:
            ctl = catalog.MessageCatalog(filename=file)
            language = utils.getLanguage(product, file)
            lang_ctl = po_ctls.get(language, None)
            if lang_ctl is None:
                po_ctls[language] = ctl
            else:
                po_ctls[language].merge(ctl)

    if not po_ctls:
        short_usage(1, 'Error: No po files found.')

    po_catalogs = []
    # flatten to list and sort
    keys = po_ctls.keys()
    keys.sort()
    for key in keys:
        po_catalogs.append(po_ctls[key])

    visualisation.make_listing(pot_ctl, po_catalogs, table=table)


def main():
    if len(sys.argv) == 1:
        usage(0)

    commands = {'find-untranslated': find_untranslated,
                'rebuild-pot': rebuild_pot,
                'merge': merge,
                'sync': sync,
                'filter': filter,
                'admix': admix,
                'list': list}

    command = sys.argv[1]

    try:
        fun = commands[command]
    except KeyError:
        if command in ('-h', '--help'):
            fun = lambda: usage(0)
        else:
            print >> sys.stderr, 'Unknown command %s' % command
            sys.exit(1)

    fun()

if __name__ == '__main__':
    main()
