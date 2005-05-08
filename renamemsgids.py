"""
scans a pot file for msg ids to renname and replaces
replaces them in the apropriate files
usage:
    change to a product directory and issue
    python ../i18ndude/renamemsgids.py xyz.pot
    adapt the path as neccessary


renamemsgids.py works on potfiles as constructed by
i18ndude rebuild-pot.
Where ever in a msg id block a new_msgid is found
msgid is replaced in all files indicated by the #:from
marker.
In the pot file all msgid's are renamed, and the new_msgid's removed.

The following block is processed like this:
    In the files test2.pt, skins/ZEHNDER/prefs/prefs_user_details.pt
all i18n:translate="yes" are replaced  with i18n:translate="yes"


#: from test2.pt
#. <label for="cb_formtooltips" i18n:translate="yes">
#.  Yes
#. </label>
#: from skins/ZEHNDER/prefs/prefs_user_details.pt
#. <label for="cb_visible_ids" i18n:translate="yes">
#.  Yes
#. </label>
msgid "yes"
new_msgid "yes_new"
msgstr ""


_robert_ robert@redcor.ch
"""
import sys, os

input_stack = []
output_stack = []

def addLinesToOutput(lines):
    # add line to buffered outbut
    global output_stack
    if type(lines) == type(''):
        lines = [lines]
    output_stack += lines

def putBack(line):
    # put line back at the end of the input stack
    global input_stack
    input_stack.append(line)

def getLineFromInput():
    # get from the buffered file
    return input_stack.pop()

def getMessageBlock():
    # first we get all lines until we find one
    # starting with '#: from' which marks the start
    # of a new block
    i18ntag_repl = 'i18n:translate=%s'
    line = ''
    blockstart = '#: from'
    while input_stack and not line.startswith(blockstart):
        line = getLineFromInput().strip()
        addLinesToOutput(line)
    # now we are at the start of a text block
    # we repeat the same procedure but put the line starting the next
    # message block back to the input stack
    # in the process we keep information what file to change and
    # whether we have to change it
    filenames = []
    msgid = ''
    new_msgid = ''
    msginfo_found = 0
    if line.startswith(blockstart):
        filenames.append(line[len(blockstart):].strip())
    line = '' # prepare this run
    local_stack = []
    msidIndex = 0
    while input_stack:
        # when the "real" msginfo block has not yet
        # been found we read everything
        line = getLineFromInput().strip()
        if not msginfo_found:
            msginfo_found = (not line.startswith('#'))
        # when we are still in the lines defining the context
        # we just check for further files
        if not msginfo_found:
            if line.startswith(blockstart):
                filenames.append(line[len(blockstart):].strip())
            local_stack.append(line)
        else:
            # put line with blockstart back but
            # prevent adding line with blockstart twice
            if (not line.startswith(blockstart)) and (not line.startswith('new_msgid')):
                local_stack.append(line)
            elif line.startswith(blockstart):
                putBack(line)
                # we are at the end of this block
                break
            # collect info
            if line.startswith('msgid'):
                msgid = line[len('msgid'):].strip()
                msidIndex = len(local_stack) - 1
            elif line.startswith('new_msgid'):
                new_msgid = line[len('new_msgid'):].strip()
    # replace msgid in local stck and add it to output
    if msidIndex and len(new_msgid):
        local_stack[msidIndex] = local_stack[msidIndex].replace(msgid, new_msgid)
    addLinesToOutput(local_stack)
    # if we found a new msg id we have to get the file(s) and replace it
    processed_files = []
    if msgid and new_msgid and filenames:
        for filename in filenames:
            if not os.path.isfile(filename):
                continue
            processed_files.append(filename)
            f = open(filename, 'r')
            src = f.read()
            f.close()
            src = src.replace(i18ntag_repl % msgid, i18ntag_repl % new_msgid)
            f = open(filename, 'w')
            f.write(src)
            f.close()
    return(processed_files, (msgid, new_msgid))

def process_file(filename):
    global input_stack
    global output_stack
    # we need a counter to create ids
    counter = 0
    if not os.path.isfile(filename):
        return
    f = open(filename, 'r')
    input_stack = f.readlines()
    # we pop from the end, so we must reverse
    input_stack.reverse()
    f.close()

    # start processing
    must_write = 0
    processed_files = []
    changed_ids = []
    while input_stack:
        pfs,cids = getMessageBlock()
        # if no new ids found just go on
        if cids[1]:
            processed_files += pfs
            changed_ids.append(cids)
    if processed_files:
        output_text = '\n'.join(output_stack)
        #os.rename(filename, filename + '.ori')
        f = open(filename, 'w')
        f.write(output_text)
        f.close()

    print 'processed files :', processed_files, '\n'
    print 'changed ids :', changed_ids

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print  'usage:replacetaginfiles file.po'
        sys.exit(1)
    process_file(sys.argv[1])
