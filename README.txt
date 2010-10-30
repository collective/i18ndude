Call i18ndude with the --help argument to see what it can do for you.

==============
Usage Examples
==============

-   Say you want i18ndude to scan for all page templates in directory 'skins/'
    and print the report to stdout:

    $ ./i18ndude find-untranslated `find skins/ -iregex '.*\..?pt$'`


-   If you wanted to synchronize your master pot-file (say 'plone.pot') with a
    language-specific version (say 'plone-eo.po'), you could go about it like
    this:

    $ ./i18ndude sync --pot plone.pot plone-eo.po
    
    Note that, unless you provide the -s option here, i18ndude will append
    to 'plone-eo.po' a report including all msgids that were added and all that
    were removed. Delete that report when you're done.

========
Commands
========

See also the output of i18ndude --help 

rebuild-pot --pot <filename> [--create <domain> [--merge <filename>] -s] directory
---------------------------------------------------------------------

Assuming you are in Plone's skins directory and you want to build a fresh
PO template from all Page Templates you can call i18ndude like this:

    i18ndude rebuild-pot --pot ~/tmp/plone.pot \
    --create plone -s . 2>~/tmp/report.txt

This will warn about any 'unnecessary literal msgids', which should be replaced
by a symbolic id. E.g.

    <h1 i18n:translate="">
        Create a Group      
    </h1>

should be replaced to be

    <h1 i18n:translate="heading_creategroup">
        Create a Group
    </h1>

If the POT already contains the string "Create a Group" with a different id
(but with the same prefix), reuse it.

Note that i18ndude has its bugs: Not all reports of 'Unneeded literal msgid'
are true, e.g.:

    <tal:block content="error_workflow_action" i18n:translate="">
        Error
    </tal:block>

    <td i18n:translate="">
        <span tal:replace="items/action"/>
    </td>

You need to put these literal ids into the manual pot-file. Also, all reports
of 'Assuming rendered msgid in ...' signal a source of literal msgids.

http://www.plone.org/development/i18n/translators-guidelines lists the
prefixes to use for msgids.

sync --pot <filename> [-s] file1 [file2 ...]
--------------------------------------------

It is recommended to use msgmerge(1) instead of sync.

Note that 'sync' has only been tested sparsely. Please report any bugs
or suggestions that you might have. When writing out the .po- file,
sync orders entries by msgid, where 'literal' msgids come last.
Therefore it is not possible to keep up with comments that are of
chronological nature. ERASE THESE from the pot.

=========
Utilities
=========
There are two utilities.
- replaceemptytags.py
- renamemsgids.py
Their usage is explained in their headers.

===========
Development
===========

i18ndude is being developed at http://plone.org/products/i18ndude
