import os
import subprocess

# Two parameters determine the wrapping of lines.  If WRAP is False,
# no wrapping is done.  If WRAP is True, the lines will be wrapped at
# MAX_WIDTH characters.  Both values can be changed by the script,
# based on command line arguments.
#
# By default no wrapping is done, as that has always been the default
# and only behaviour.  This may change in the future.
MAX_WIDTH = 79
WRAP = False


def getPoFiles(product, all=False):
    """Returns all product*.po files in the current folder.
    """
    # First try old style i18n directory that has all .pot and .po files in
    # one directory.
    files = os.listdir(os.curdir)
    if all:
        files = [file for file in files if file.startswith('%s-' % product)
                 and file.endswith('.po')]
    else:
        files = [file for file in files if file.startswith('%s-' % product)
                 and file.endswith('.po') and file != '%s-en.po' % product]
    if files:
        return files
    # We may be in a locales directory.
    po_name = '%s.po' % product
    files = []
    for dirpath, dirnames, filenames in os.walk('.'):
        # Look for LC_MESSAGES directories
        if dirpath.split(os.path.sep)[-1] != 'LC_MESSAGES':
            continue
        if po_name in filenames:
            files.append(os.path.join(dirpath, po_name))
    return files


def getPotFiles(product=None, all=False):
    """Returns all pot files in the current folder.
    Normally it doesn't return manual.pots and generated.pots.
    """
    files = os.listdir(os.curdir)
    if all:
        files = [f for f in files if f.endswith('.pot')]
    else:
        files = [
            f for f in files
            if f.endswith('.pot')
            and not f[:-4].endswith('manual')
            and not f[:-4].endswith('generated')
        ]
    if product is not None:
        files = [f for f in files if f.startswith('%s.pot' % product)]
    return files


def getPoFilesAsCmdLine(product):
    files = getPoFiles(product)
    filestring = ''
    for file in files:
        filestring += file + ' '
    return filestring.rstrip()


def getPoFilesByLanguageCode(lang):
    """Returns all po files which ends with given language code.
    """
    files = os.listdir(os.curdir)
    files = [file for file in files if file.endswith(
        '.po') and file[:-3].endswith(lang)]
    return files


def getLanguage(product, file):
    """Returns the language part of a po-file.
    """
    lang = None
    if file.endswith('.po'):
        if file.startswith(product):
            lang = '-'.join(file.split('-')[1:])[:-3]
        else:
            # Get directory name in case of locales structure:
            # lang/LC_MESSAGES/product.po
            lc_found = False
            for part in reversed(file.split(os.path.sep)):
                if lc_found:
                    lang = part
                    break
                if part == 'LC_MESSAGES':
                    lc_found = True
    return lang


def getProduct(file):
    """Returns the product part of a file. We assume files to be something like
    domain-language.po.
    Example: atcontenttypes-pt-br.po
    """
    assert file.endswith('.po') or file.endswith('.pot')

    file = file.split('.')[0]  # strip of ending
    file = file.split('-')[0]  # only take product

    return file


def wrapAndQuoteString(value):
    """Wrap a string in multiple quoted lines.
    """
    if not value:
        return u'""'
    # Wrap over multiple lines if needed.
    lineparts = wrapString(value)
    if len(lineparts) == 1:
        return u'"{0}"'.format(lineparts[0])
    # We expect the first line to be empty.  Remove it.
    if not lineparts[0]:
        lineparts.pop(0)
    # Quote all and separate them by newlines.
    newline = u'"\n"'.join(lineparts)
    return u'"{0}"'.format(newline)


def wrapString(value):
    """Wrap a string in multiple lines.

    They should have a length of at most MAX_WIDTH, minus 3 for the
    start quote, end quote and a space before the end quote, although
    that last one should not be needed for the last word.

    Returns a list of strings.  All but the last will have a space at
    the end.
    """
    if not WRAP:
        return [value]
    # Determine the maximum line length.  At first we only reserve
    # room for the two enclosing quotes.
    max_len = MAX_WIDTH - 2
    # For a single line the maximum length is shorter, it has to account
    # for the 'msgstr ' that goes before the string.
    single_line_max_len = max_len - len('msgstr ')
    # Maybe we have it easy.
    if max_len <= 0 or len(value) <= single_line_max_len:
        return [value]
    # The line maybe is just in between max_len and single_line_max_len
    if len(value) <= max_len:
        return [u'', value]
    # No, the value does not fit on one line.  This means we need to
    # reserve room for a space at the end of all but the last line.
    max_len -= 1
    words = value.split(u' ')
    len_words = len(words)
    # We always start with an empty first line
    lines = [u'']
    line = u''
    for index, word in enumerate(words):
        if index == len_words - 1:
            # This is the last word.  The last line needs no space at
            # the end, so we are allowed to use one more character.
            max_len += 1
        if not line:
            new_line = word
        else:
            new_line = u'{0} {1}'.format(line, word)
        if len(new_line) <= max_len or not line:
            # There is room or we had an empty line and the current
            # single word is already too large so we accept it as a
            # line anyway.  Use the new line and continue with the
            # next word.
            line = new_line
            continue
        # There is no more room so we store the line.  If it is not
        # empty it should end with a space.
        if line:
            line += u' '
        lines.append(line)
        # Start a fresh line with the current word.
        line = word
    # The last line has not been added yet.
    lines.append(line)
    return lines


def prepare_cli_documentation(data):
    """Update the command line docs in the docs dir.

    This uses a hook from zest.releaser to update some documentation
    when doing a release.  See our setup.py and setup.cfg.
    """
    if data['name'] != 'i18ndude':
        # We're available everywhere, but we're only intended to be
        # used when we release i18ndude.
        return
    target = os.path.join(data['workingdir'], 'docs',
                          'command.rst')
    marker = '.. ### AUTOGENERATED FROM HERE ###'
    result = []
    for line in open(target).readlines():
        line = line.rstrip()
        if line == marker:
            break
        result.append(line)
    result.append(marker)
    result.append('')

    def indent(text):
        result = []
        for line in text.splitlines():
            if line:
                result.append('  ' + line)
            else:
                result.append('')
        return result

    base_cmd = 'bin/i18ndude'
    # Add result off calling bin/i18ndude --help
    result.append('i18ndude')
    result.append('--------')
    result.append("\n::\n")
    res = subprocess.check_output([base_cmd, '--help'])
    result.extend(indent(res))
    # Same for the subcommands.
    subcommands = [
        'find-untranslated',
        'rebuild-pot',
        'merge',
        'sync',
        'filter',
        'admix',
        'list',
        'trmerge']
    for sub in subcommands:
        result.append('')
        result.append(sub)
        result.append('-' * len(sub))
        result.append("\n::\n")
        res = subprocess.check_output([base_cmd, sub, '--help'])
        result.extend(indent(res))

    result.append('')
    open(target, 'wb').write('\n'.join(result))
    print "Wrote command line documentation to", target

    # If there is a diff, we want to commit it.
    from zest.releaser import choose
    from zest.releaser.utils import ask, execute_command
    vcs = choose.version_control()
    diff_cmd = vcs.cmd_diff()
    diff = execute_command(diff_cmd)
    if diff.strip():
        print "The %r:\n\n%s\n" % (diff_cmd, diff)
        if ask("OK to commit this"):
            msg = "Wrote command line documentation."
            commit_cmd = vcs.cmd_commit(msg)
            print execute_command(commit_cmd)


def quote(s):
    """Quote if string has spaces."""

    if [ch for ch in s if ch.isspace()]:
        return '"%s"' % s
    else:
        return s
