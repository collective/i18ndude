import os
import sys

# Max line width for msgid and msgstr lines.
DEFAULT_MAX_WIDTH = 79
MAX_WIDTH = os.environ.get('PO_MAX_WIDTH', '')
if MAX_WIDTH:
    try:
        MAX_WIDTH = int(MAX_WIDTH)
    except ValueError:
        print >> sys.stderr, "PO_MAX_WIDTH ignored, as it is no integer."
        MAX_WIDTH = DEFAULT_MAX_WIDTH
else:
    MAX_WIDTH = DEFAULT_MAX_WIDTH


def getPoFiles(product, all=False):
    """ Returns all product*.po files in the current folder """
    files = os.listdir(os.curdir)
    if all:
        files = [file for file in files if file.startswith('%s-' % product) and file.endswith('.po')]
    else:
        files = [file for file in files if file.startswith('%s-' % product) and file.endswith('.po') and file != '%s-en.po' % product]
    return files


def getPotFiles(product=None, all=False):
    """ Returns all pot files in the current folder
        Normally it doesn't return manual.pots and generated.pots
    """
    files = os.listdir(os.curdir)
    if all:
        files = [f for f in files if f.endswith('.pot')]
    else:
        files = [f for f in files if f.endswith('.pot') and not f[:-4].endswith('manual') and not f[:-4].endswith('generated')]
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
    """ Returns all po files which ends with given language code."""
    files = os.listdir(os.curdir)
    files = [file for file in files if file.endswith('.po') and file[:-3].endswith(lang)]
    return files


def getLanguage(product, file):
    """ Returns the language part of a po-file """
    lang = None
    if file.endswith('.po'):
        if file.startswith(product):
            lang = '-'.join(file.split('-')[1:])[:-3]
    return lang


def getProduct(file):
    """ Returns the product part of a file. We assume files to be something like domain-language.po.
        Example: atcontenttypes-pt-br.po
    """
    assert file.endswith('.po') or file.endswith('.pot')

    file = file.split('.')[0]  # strip of ending
    file = file.split('-')[0]  # only take product

    return file


def wrapString(value):
    """Wrap a string in multiple lines.

    They should have a length of at most MAX_WIDTH, minus 3 for the
    start quote, end quote and a space before the end quote, although
    that last one should not be needed for the last word.

    Returns a list of strings.  All but the last will have a space at
    the end.
    """
    # Determine the maximum line length.  At first we only reserve
    # room for the two enclosing quotes.
    max_len = MAX_WIDTH - 2
    # Maybe we have it easy.
    if len(value) <= max_len or max_len <= 0:
        return [value]
    # No, the value does not fit on one line.  This means we need to
    # reserve room for a space at the end of all but the last line.
    max_len -= 1
    words = value.split(' ')
    len_words = len(words)
    # We always start with an empty first line
    lines = ['']
    line = ''
    for index, word in enumerate(words):
        if index == len_words -1:
            # This is the last word.  The last line needs no space at
            # the end, so we are allowed to use one more character.
            max_len += 1
        if not line:
            new_line = word
        else:
            new_line = '%s %s' %(line, word)
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
            line += ' '
        lines.append(line)
        # Start a fresh line with the current word.
        line = word
    # The last line has not been added yet.
    lines.append(line)
    return lines
