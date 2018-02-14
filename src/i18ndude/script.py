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

import argparse
import os
import sys
import textwrap
import xml.sax

from i18ndude import common, untranslated, catalog, visualisation, utils

PY3 = sys.version_info > (3,)
if PY3:
    unicode = str

# Define a parent parser for the wrapping arguments.  This is shared
# by a few commands.  Note: if you use this parser, you need to call
# the parse_wrapping_arguments function somewhere in the handling of
# your command.
wrapper_parser = argparse.ArgumentParser(add_help=False)
wrapping_group = wrapper_parser.add_mutually_exclusive_group()
wrapping_group.add_argument(
    '--wrap', action='store_true', help="Wrap long lines.")
wrapping_group.add_argument(
    '--no-wrap', action='store_true',
    help="Do not wrap long lines. This is the default.")
wrapper_parser.add_argument(
    '--width', metavar='NUMBER', type=int,
    help="Set output page width. Default is %d." % utils.MAX_WIDTH)


def parse_wrapping_arguments(arguments):
    """Parse the arguments that handle wrapping.

    Based on the arguments we can store the result in utils.MAX_WIDTH
    and utils.WRAP.  If the arguments are not set, we do nothing: the
    default values of those variables are used.
    """
    if 'width' in arguments and arguments.width:
        utils.MAX_WIDTH = arguments.width
    if 'wrap' in arguments and arguments.wrap:
        utils.WRAP = True
    elif 'no_wrap' in arguments and arguments.no_wrap:
        utils.WRAP = False


def short_usage(code, msg=''):
    if msg:
        sys.stderr.write(msg)
    sys.stderr.write(u"Type i18ndude -h<Enter> to see the help.")
    sys.exit(code)


def filter_isfile(files):
    result = []
    for name in files:  # parse file by file
        name = name.strip()
        if os.path.isdir(name):  # descend recursively
            subdirs = []
            for subpath in os.listdir(name):
                if subpath.startswith('.'):
                    # ignore hidden file
                    continue
                path = os.path.join(name, subpath)
                if (os.path.isdir(path) or
                        os.path.splitext(subpath)[1].endswith('pt')):
                    subdirs.append(path)
            result += filter_isfile(subdirs)

        elif not os.path.isfile(name):
            sys.stderr.write(
                'Warning: %s is not a file or is ignored.' % name)

        else:
            result.append(name)
    return result


def find_untranslated_parser(subparsers):
    """Argument parser for find-untranslated command.

    find-untranslated [-s|-n] [file1 [file2 ...]]
    """

    description = """
    Provide a list of ZPT filenames and I will output a report of places
    where I suspect untranslated messages, i.e. tags for which
    "i18n:translate" or "i18n:attributes" are missing.

    If you provide the -s option, the report will only contain a summary
    of errors and warnings for each file (or no output if there are no
    errors or warnings). If you provide the -n option, the report will
    contain only the errors for each file.

    You can mark tags to be ignored for this translation check by
    setting the "i18n:ignore" attribute on the tag. Same for
    attributes with "i18n:ignore-attributes". Note that i18ndude may
    be happy with this, but your template engine may fail when trying
    to render a template containing those ignore hints.  You need
    Chameleon 2.23 or higher, or the to be released zope.tal 4.1.2.
    """
    parser = subparsers.add_parser(
        'find-untranslated',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description
    )
    parser.add_argument('-s', '--silent', action='store_true', help=(
        "The report will only contain a summary of errors and warnings for "
        "each file (or no output if there are no errors or warnings)."))
    parser.add_argument('-n', '--nosummary', action='store_true', help=(
        "The report will contain only the errors for each file."))
    parser.add_argument('files', nargs='*', help="list of ZPT filenames")
    parser.set_defaults(func=find_untranslated)
    return parser


def find_untranslated(arguments):
    parser = xml.sax.make_parser(['expat'])
    # disable external validation to make it work without network access
    parser.setFeature(xml.sax.handler.feature_external_ges, False)
    parser.setFeature(xml.sax.handler.feature_external_pes, False)
    handler = untranslated.VerboseHandler(parser)  # default

    if arguments.silent:
        handler = untranslated.SilentHandler(parser)
    elif arguments.nosummary:
        handler = untranslated.NoSummaryVerboseHandler(parser)

    parser.setContentHandler(handler)
    errors = 0
    for filename in filter_isfile(arguments.files):  # parse file by file
        with open(filename) as myfile:
            if not myfile.read().strip():
                continue
        # Reinitialize the handler, resetting errors.
        handler.set_filename(filename)
        file_errors = []
        success = False
        for content in common.present_file_contents(filename):
            if content is None:
                continue
            if isinstance(content, list):
                # These are errors.
                file_errors.extend(content)
                continue
            # Reinitialize the handler, resetting errors.
            handler.set_filename(filename)
            try:
                parser.parse(content)
            except KeyboardInterrupt:
                sys.stderr.write('Interrupted by user.')
                sys.exit(1)
            except xml.sax.SAXException as error:
                file_errors.append(error)
                continue
            except Exception as error:
                file_errors.append(error)
                continue
            else:
                # We have successfully parsed the file.
                success = True
                # We can safely print the output.
                handler.show_output()
                # No need for a run with another parser.
                break
            finally:
                handler.clear_output()
        # Note that the error stats of the handler get reset to zero
        # when starting on a new document, so we ask about errors
        # after each document.
        if handler.has_errors():
            # So some untranslated strings were found.
            errors += 1
        if success:
            # next file
            continue
        if file_errors:
            errors += 1
            report = 'ERRORs found trying to parse document in various ways:\n'
            for error in file_errors:
                report += '%s\n' % error
            handler.log(report, 'FATAL')
    return errors


def rebuild_pot_parser(subparsers):
    """Argument parser for rebuild-pot command.

    rebuild-pot --pot <filename> --create <domain>
        [--merge <filename> [--merge2 <filename>]]
        [--exclude="<ignore1> <ignore2> ..."] path [path2 ...]
    """

    description = """
    Given a pot-file via the --pot option you can specify one or more
    directories which including all sub-folders will be searched for
    PageTemplates (*.*pt) and Python scripts (*.*py).

    Make sure you have a backup copy of the original pot-file in case
    you need to fill back in ids by hand.

    If you specify a domain in --create I will create the pot file and
    look for messages for that domain.  Otherwise I will take the
    domain from the Domain header in the given pot file and keep the
    headers from the file as base for a new pot file.

    If you give me an additional pot-file with the --merge <filename>
    option, I try to merge these msgids into the target-pot file
    afterwards. If a msgid already exists in the ones I found in the
    ZPTs, I'll warn you and ignore that msgid. I take the mime-header
    from this additional pot-file. If you provide a second pot-file via
    --merge2 <filename> I'll merge this into the first merge's result

    You can also provide a list of filenames (or regular expressions for
    filenames) which should not be included by using the --exclude argument,
    which takes a whitespace delimited list of files (or regular expressions
    for files).
    """
    parser = subparsers.add_parser(
        'rebuild-pot',
        parents=[wrapper_parser],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description
    )
    parser.add_argument('-p', '--pot', metavar='filename',
                        dest='pot_fn', required=True)
    parser.add_argument('-c', '--create', metavar='domain',
                        dest='create_domain', required=False)
    parser.add_argument('-m', '--merge', metavar='filename', dest='merge_fn')
    parser.add_argument('--merge2', metavar='filename', dest='merge2_fn')
    parser.add_argument(
        '--exclude', metavar='"<ignore1> <ignore2> ..."', default='')
    parser.add_argument('path', nargs='*')
    parser.set_defaults(func=rebuild_pot)
    return parser


def rebuild_pot(arguments):
    merge_ctl = None

    # Determine final argument values.
    create_domain = arguments.create_domain
    exclude = arguments.exclude and tuple(arguments.exclude.split()) or ()
    pot_fn = arguments.pot_fn
    merge_fn = arguments.merge_fn
    merge2_fn = arguments.merge2_fn
    if merge2_fn == merge_fn:
        merge2_fn = False
    path = arguments.path

    try:
        if create_domain is not None:
            orig_ctl = catalog.MessageCatalog(domain=create_domain)
        else:
            orig_ctl = catalog.MessageCatalog(filename=pot_fn)
            create_domain = orig_ctl.domain
        if merge_fn:
            merge_ctl = catalog.MessageCatalog(filename=merge_fn)
        if merge2_fn:
            merge2_ctl = catalog.MessageCatalog(filename=merge2_fn)
        ptreader = catalog.PTReader(path, create_domain, exclude=exclude)
        pyreader = catalog.PYReader(path, create_domain, exclude=exclude)
        gsreader = catalog.GSReader(path, create_domain, exclude=exclude)
        zcmlreader = catalog.ZCMLReader(path, create_domain, exclude=exclude)
    except IOError as e:
        short_usage(0, 'I/O Error: %s' % e)

    # Read the data.
    ptreader.read()
    pyreader.read()
    gsreader.read()
    zcmlreader.read()

    domain = orig_ctl.domain

    ptctl = pyctl = gsctl = zcmlctl = {}
    if domain in ptreader.catalogs:
        ptctl = ptreader.catalogs[domain]
        for key in orig_ctl.keys():
            if key in ptctl:
                # preserve comments
                ptctl[key].comments = ptctl[
                    key].comments + orig_ctl.getComments(key)

    if domain in pyreader.catalogs:
        pyctl = pyreader.catalogs[domain]
        for key in orig_ctl.keys():
            if key in pyctl:
                # preserve comments
                pyctl[key].comments = pyctl[
                    key].comments + orig_ctl.getComments(key)

    if domain in gsreader.catalogs:
        gsctl = gsreader.catalogs[domain]
        # XXX Preserve comments?

    if domain in zcmlreader.catalogs:
        zcmlctl = zcmlreader.catalogs[domain]
        # XXX Preserve comments?

    if not (ptctl or pyctl or gsctl or zcmlctl):
        short_usage(0, 'No entries for domain "%s".' % domain)

    ctl = ptctl or pyctl or gsctl or zcmlctl
    if pyctl and pyctl is not ctl:
        ctl.merge(pyctl)
    if gsctl and gsctl is not ctl:
        ctl.merge(gsctl)
    if zcmlctl and zcmlctl is not ctl:
        ctl.merge(zcmlctl)

    if merge_ctl is not None:
        # use headers from merge-catalog
        ctl.commentary_header = merge_ctl.commentary_header
        ctl.mime_header = merge_ctl.mime_header
        # merge
        ctl.add_missing(merge_ctl, mergewarn=True)
    else:
        # use headers from orig-catalog
        ctl.commentary_header = orig_ctl.commentary_header
        ctl.mime_header = orig_ctl.mime_header

    if merge2_fn:
        ctl.add_missing(merge2_ctl, mergewarn=True)

    ctl.mime_header['POT-Creation-Date'] = catalog.now()
    file = open(pot_fn, 'w')
    writer = catalog.POWriter(file, ctl)
    writer.write(msgstrToComment=True)


def merge_parser(subparsers):
    """Argument parser for merge command.

    merge --pot <filename> --merge <filename> [--merge2 <filename>]
    """

    description = """
    Given a pot-file via the --pot option and a second
    pot-file with the --merge <filename> option, I try to merge
    these msgids into the target-pot file. If a msgid already
    exists, I'll warn you and ignore that msgid.

    If you provide a --merge2 <filename> I'll first merge this one
    in addition to the first one.
    """
    parser = subparsers.add_parser(
        'merge',
        parents=[wrapper_parser],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description
    )
    parser.add_argument('-p', '--pot', metavar='filename',
                        dest='pot_fn', required=True)
    parser.add_argument('-m', '--merge', metavar='filename', dest='merge_fn',
                        required=True)
    parser.add_argument('--merge2', metavar='filename', dest='merge2_fn')
    parser.set_defaults(func=merge)
    return parser


def merge(arguments):
    # Determine final argument values.
    pot_fn = arguments.pot_fn
    merge_fn = arguments.merge_fn
    merge2_fn = arguments.merge2_fn
    if merge2_fn == merge_fn:
        merge2_fn = False

    if not pot_fn:
        short_usage(1, u"No pot file specified as target with --pot.")
    if not merge_fn:
        short_usage(1, u"No potfile specified as source with --merge.")

    try:
        orig_ctl = catalog.MessageCatalog(filename=pot_fn)
        merge_ctl = catalog.MessageCatalog(filename=merge_fn)
        if merge2_fn:
            merge2_ctl = catalog.MessageCatalog(filename=merge2_fn)
    except IOError as e:
        short_usage(0, 'I/O Error: %s' % e)

    # merge
    orig_ctl.add_missing(merge_ctl, '', 1)
    if merge2_fn:
        orig_ctl.add_missing(merge2_ctl, '', 1)
    orig_ctl.mime_header['POT-Creation-Date'] = catalog.now()
    file = open(pot_fn, 'w')
    writer = catalog.POWriter(file, orig_ctl)
    writer.write(msgstrToComment=True)


def sync_parser(subparsers):
    """Argument parser for sync command.

    sync --pot <filename> file1 [file2 ...]
    """

    description = """
    Given a pot-file with the --pot option and a list of po-files I'll
    remove from the po files those message translations of which the
    msgids are not in the pot-file and add messages that the pot-file has
    but the po-file doesn't.
    """
    parser = subparsers.add_parser(
        'sync',
        parents=[wrapper_parser],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description
    )
    parser.add_argument('-p', '--pot', metavar='potfilename',
                        dest='pot_fn', required=True)
    parser.add_argument('files', nargs='+', metavar='pofilename')
    parser.set_defaults(func=sync)
    return parser


def sync(arguments):
    pot_fn = arguments.pot_fn
    if not pot_fn:
        short_usage(1, u"No pot file specified as target with --pot.")

    files = filter_isfile(arguments.files)

    try:
        pot_ctl = catalog.MessageCatalog(filename=pot_fn)
        po_ctls = [catalog.MessageCatalog(filename=fn) for fn in files]
    except IOError as e:
        short_usage(1, 'I/O Error: %s' % e)

    for po in po_ctls:
        added_msgids, removed_msgids = po.sync(pot_ctl)

        file = open(po.filename, 'w')
        writer = catalog.POWriter(file, po)
        writer.write(msgstrToComment=False, sync=True)

        print('%s: %s added, %s removed' % (po.filename,
                                            len(added_msgids),
                                            len(removed_msgids)))
        file.close()


def two_file_parser(subparsers, cmd, description):
    """Argument parser for command that takes two files.

    filter, admix and trmerge all accept two files as arguments.
    """

    parser = subparsers.add_parser(
        cmd,
        parents=[wrapper_parser],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description
    )
    parser.add_argument('file1')
    parser.add_argument('file2')
    return parser


def filter_parser(subparsers):
    """Argument parser for filter command.

    filter <file1> <file2>
    """

    description = """
    Given two pot-files I will write a copy of file1 to stdout with all
    messages removed that are also in file2, i.e. where msgids match.
    """
    parser = two_file_parser(subparsers, 'filter', description)
    parser.set_defaults(func=filter)
    return parser


def filter(arguments):
    f1_ctl = catalog.MessageCatalog(filename=arguments.file1)
    f2_ctl = catalog.MessageCatalog(filename=arguments.file2)

    for msgid in f1_ctl.keys():
        if msgid in f2_ctl:
            del f1_ctl[msgid]

    writer = catalog.POWriter(sys.stdout, f1_ctl)
    writer.write(sort=False, msgstrToComment=True)


def admix_parser(subparsers):
    """Argument parser for admix command.

    admix <file1> <file2>
    """

    description = """
    Given two po-files I will look for translated entries in file2 that
    are untranslated in file1. I add these translations (msgstrs) to
    file1. Note that this will not affect the number of entries in file1.
    The result will be on stdout.
    """
    parser = two_file_parser(subparsers, 'admix', description)
    parser.set_defaults(func=admix)
    return parser


def admix(arguments):
    base_ctl = catalog.MessageCatalog(filename=arguments.file1)
    mixin_ctl = catalog.MessageCatalog(filename=arguments.file2)

    for msgid in mixin_ctl:
        mixin_msgstr = mixin_ctl[msgid].msgstr

        if mixin_msgstr and msgid in base_ctl and not base_ctl[msgid].msgstr:
            entry = base_ctl[msgid]
            entry.msgstr = mixin_ctl[msgid].msgstr
            base_ctl[msgid] = entry

    writer = catalog.POWriter(sys.stdout, base_ctl)
    writer.write(sort=False)


def trmerge_parser(subparsers):
    """Argument parser for trmerge command.

    trmerge <file1> <file2>
    """

    description = """
    Given two po-files I will update all translations from file2 into
    file1. Missing translations are added.

    If a translation was fuzzy in file1, and there is a nonempty translation
    in file2, the fuzzy marker is removed.

    Fuzzy translations in file2 are ignored.

    The result will be on stdout.  If you want to update the first
    file in place, use a temporary file, something like this:

      i18ndude trmerge file1.po file2.po > tmp_merge && mv tmp_merge file1.po
    """
    parser = two_file_parser(subparsers, 'trmerge', description)
    parser.add_argument('-i', '--ignore-extra', action='store_true', help=(
        "Ignore extra messages: do not add msgids that are not in the "
        "original po-file. Only update translations for existing msgids."))
    parser.add_argument('--no-override', action='store_true', help=(
        "Do not override translations, only add missing translations."))
    parser.set_defaults(func=trmerge)
    return parser


def trmerge(arguments):
    base_ctl = catalog.MessageCatalog(filename=arguments.file1)
    mixin_ctl = catalog.MessageCatalog(filename=arguments.file2)

    for msgid in mixin_ctl:
        base_entry = base_ctl.get(msgid)
        if base_entry is None and arguments.ignore_extra:
            # This msgid is not in the original po-file and the user
            # has chosen to ignore it.
            continue
        mixin_entry = mixin_ctl[msgid]
        mixin_msgstr = mixin_entry.msgstr
        if not mixin_msgstr:
            # The mixin translation is empty.
            continue
        if ', fuzzy' in mixin_entry.comments:
            # The mixin translation is fuzzy.
            continue
        if (arguments.no_override
                and base_entry is not None
                and base_entry.msgstr
                and ', fuzzy' not in base_entry.comments):
            # The user does not want to override and we have an
            # existing, non-fuzzy translation.
            continue
        # Okay, we have a fine new translation.
        entry = base_entry or mixin_entry
        entry.msgstr = mixin_msgstr
        if ', fuzzy' in entry.comments:
            # The base entry was fuzzy, but the mixin has a different
            # or non-fuzzy translation.
            entry.comments.remove(', fuzzy')
        # Finally store the new entry
        base_ctl[msgid] = entry

    writer = catalog.POWriter(sys.stdout, base_ctl)
    writer.write(sort=False)


def list_parser(subparsers):
    """Argument parser for list command.

    list --products <product1> [<product2> ...]
    """

    description = """
    This will create a simple listing that displays how much of the
    combined products pot's is translated for each language. Run this
    from the directory containing the pot-files. The product name is
    normally a domain name.
    """
    parser = subparsers.add_parser(
        'list',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description
    )
    parser.add_argument('-p', '--products', metavar='product', nargs='+',
                        required=True)
    parser.add_argument('-t', '--table', action='store_true')
    parser.set_defaults(func=arg_list)
    return parser


def arg_list(arguments):
    table = arguments.table
    products = arguments.products

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
    keys = sorted(po_ctls.keys())
    for key in keys:
        po_catalogs.append(po_ctls[key])

    visualisation.make_listing(pot_ctl, po_catalogs, table=table)


def main():
    description = """
    i18ndude performs various tasks related to ZPT's, Python Scripts
    and i18n.

    Its main task is to extract translation strings (msgids) into a
    .pot file (with the 'rebuild-pot' command), and sync the .pot file
    with .po files (with the 'sync' command).

    Call i18ndude with one of the listed subcommands followed by
    --help to get help for that subcommand.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(description))
    subparsers = parser.add_subparsers(title='subcommands')
    # Add subparsers.
    find_untranslated_parser(subparsers)
    rebuild_pot_parser(subparsers)
    merge_parser(subparsers)
    sync_parser(subparsers)
    filter_parser(subparsers)
    admix_parser(subparsers)
    list_parser(subparsers)
    trmerge_parser(subparsers)
    # Parse the arguments.
    arguments = parser.parse_args(sys.argv[1:])
    # Special handling for the wrapping arguments, if any.
    parse_wrapping_arguments(arguments)
    # Call the function of the chosen command with the arguments.
    errors = arguments.func(arguments)
    if errors:
        sys.exit(1)

if __name__ == '__main__':
    main()
