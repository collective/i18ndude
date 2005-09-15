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

See the output of i18ndude --help

=========
Utilities
=========
There are two utilities, which aren't tested nor supported. Run them at your
own risk.
- replaceemptytags.py
- renamemsgids.py
Their usage is explained in their headers.

===========
Development
===========

i18ndude is being developed at http://plone.org/products/i18ndude
