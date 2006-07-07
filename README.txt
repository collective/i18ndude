i18ndude package readme
=======================

Overview
--------

Call i18ndude with the --help argument to see what it can do for you.

Usage Examples
--------------

  - Say you want i18ndude to scan for all page templates in directory 'skins/'
    and print the report to stdout:

    $ ./i18ndude find-untranslated `find skins/ -iregex '.*\..?pt$'`

  - If you wanted to synchronize your master pot-file (say 'plone.pot') with a
    language-specific version (say 'plone-eo.po'), you could go about it like
    this:

    $ ./i18ndude sync --pot plone.pot plone-eo.po
    
Commands
--------

See the output of i18ndude --help

Development
-----------

i18ndude is being developed at http://plone.org/products/i18ndude
