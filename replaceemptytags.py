"""
    scans a file and replaces empty msgids
    This is done by either creating a msgid from the
    actual text or from the filename and a sequence number.
    The former is used when the i18n:translate="" and the
    msgstr are on the same line.

    usage:
        change to a product directory and issue
        python ../i18ndude/replaceemptytags.py `find skins/ -iregex '.*\..?pt$'`
        adapt the path as neccessary

Afterwards you can create a po file with i18ndud rebuild-pot.
Scan the created files for ungainly msgids. These you can replace
using renamemsgids.py.
Look in the head of that file for instructions how to use it.

    _robert_ robert@redcor.ch

adapted make ids lowercase and spaces replaced by underscores
<         <span i18n:translate="">Visible Members</span>:
---
>         <span i18n:translate="visible_members">Visible Members</span>:
"""
import sys, os

input_stack = []
output_stack = []

def addLineToOutput(line):
    # add line to buffered outbut
    global output_stack
    output_stack.append(line)

def getLineFromInput():
    # get from the buffered file
    return input_stack.pop()

def process_line(line, filename, counter):
    replace_text = ''
    i18ntag = 'i18n:translate=""'
    i18ntag_repl = 'i18n:translate="%s"'
    pos_trans = line.find(i18ntag)
    did_change = 0
    if pos_trans > -1:
        pos_gt = line.find('>', pos_trans)
        if pos_gt > -1:
            # we probably can construct an id
            pos_lt = line.find('<', pos_gt)
            if pos_lt > -1:
                replace_text = line[pos_gt+1:pos_lt].strip().lower().replace(' ', '_')
        # if replace_text is still empty we must contruct id fom filename
        if not replace_text:
            counter += 1
            filename = filename.replace('.','_')
            filename = filename.replace(os.sep,'_')
            replace_text = filename + '_%s' % counter
    # if we have a repcetext weave it into the line
    if replace_text:
        did_change = 1
        line = line.replace(i18ntag, i18ntag_repl % replace_text)
    # add line to output stack
    addLineToOutput(line)
    return (did_change, counter)


def process_file(filename):
    global input_stack
    global output_stack
    # we need a counter to create ids
    counter = 0
    if not os.path.isfile(filename):
        return
    f = open(filename, 'r')
    input_stack = f.readlines()
    f.close()

    # start processing
    must_write = 0
    while input_stack:
        line = getLineFromInput()
        did_change, counter = process_line(line, filename, counter)
        if did_change:
            must_write = 1

    if must_write:
        output_stack.reverse()
        output_text = ''.join(output_stack)
        os.rename(filename, filename + '.ori')
        f = open(filename, 'w')
        f.write(output_text)
        f.close()
    # prepare output_stack for next file
    output_stack = []
    return must_write





if __name__ == '__main__':
    if len(sys.argv) < 2:
        print  'usage:python replaceemtytags files'
        sys.exit(1)
    counter = 0
    written = 0
    for arg in sys.argv[1:]:
        written += process_file(arg)
        counter +=1
    print "processed %s files, changed %s of them" % (counter, written)
