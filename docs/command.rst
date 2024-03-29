Command line interface
======================

These are the various command line options.

.. ### AUTOGENERATED FROM HERE ###

i18ndude
--------

::

  usage: i18ndude [-h]
                  {find-untranslated,rebuild-pot,merge,sync,filter,admix,list,trmerge}
                  ...

  i18ndude performs various tasks related to ZPT's, Python Scripts
  and i18n.

  Its main task is to extract translation strings (msgids) into a
  .pot file (with the 'rebuild-pot' command), and sync the .pot file
  with .po files (with the 'sync' command).

  Call i18ndude with one of the listed subcommands followed by
  --help to get help for that subcommand.

  options:
    -h, --help            show this help message and exit

  subcommands:
    {find-untranslated,rebuild-pot,merge,sync,filter,admix,list,trmerge}

find-untranslated
-----------------

::

  usage: i18ndude find-untranslated [-h] [-s] [-n] [files ...]

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
      

  positional arguments:
    files            list of ZPT filenames

  options:
    -h, --help       show this help message and exit
    -s, --silent     The report will only contain a summary of errors and
                     warnings for each file (or no output if there are no errors
                     or warnings).
    -n, --nosummary  The report will contain only the errors for each file.

rebuild-pot
-----------

::

  usage: i18ndude rebuild-pot [-h] [--wrap | --no-wrap] [--width NUMBER] -p
                              filename [-c domain] [-m filename]
                              [--merge2 filename]
                              [--exclude "<ignore1> <ignore2> ..."]
                              [--no-line-numbers] [--line-numbers]
                              [path ...]

      Given a pot-file via the --pot option you can specify one or more
      directories which including all sub-folders will be searched for
      PageTemplates (*.*pt) and Python scripts (*.*py).

      Make sure you have a backup copy of the original pot-file in case
      you need to fill back in ids by hand.

      If you specify a domain in --create I will create the pot file and
      look for messages for that domain.  Otherwise I will take the
      domain from the Domain header in the given pot file and keep the
      headers from the file as base for a new pot file.

      Note that in Python files we simply look for text within an underscore
      method: _("...").  We do not know which domain this is.
      If this finds text from a domain that you do not want to find,
      you should give the underscore method for the unwanted domain
      a different name, for example:

        from zope.i18nmessageid import MessageFactory
        PMF = MessageFactory("plone")
        PMF("...")

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

      By default we add a comment showing references to file paths and line numbers
      that contain the message, like this:

          #: ./browser.py:32

      You can suppress the line numbers by using the --no-line-numbers option.
      The default might change in the future.  If you love line numbers, you can
      add --line-numbers to be sure you keep them when you get a newer version
      of i18ndude.  If you specify both options, the last one wins.
      

  positional arguments:
    path

  options:
    -h, --help            show this help message and exit
    --wrap                Wrap long lines.
    --no-wrap             Do not wrap long lines. This is the default.
    --width NUMBER        Set output page width. Default is 79.
    -p filename, --pot filename
    -c domain, --create domain
    -m filename, --merge filename
    --merge2 filename
    --exclude "<ignore1> <ignore2> ..."
    --no-line-numbers
    --line-numbers

merge
-----

::

  usage: i18ndude merge [-h] [--wrap | --no-wrap] [--width NUMBER] -p filename
                        -m filename [--merge2 filename]

      Given a pot-file via the --pot option and a second
      pot-file with the --merge <filename> option, I try to merge
      these msgids into the target-pot file. If a msgid already
      exists, I'll warn you and ignore that msgid.

      If you provide a --merge2 <filename> I'll first merge this one
      in addition to the first one.
      

  options:
    -h, --help            show this help message and exit
    --wrap                Wrap long lines.
    --no-wrap             Do not wrap long lines. This is the default.
    --width NUMBER        Set output page width. Default is 79.
    -p filename, --pot filename
    -m filename, --merge filename
    --merge2 filename

sync
----

::

  usage: i18ndude sync [-h] [--wrap | --no-wrap] [--width NUMBER] -p potfilename
                       pofilename [pofilename ...]

      Given a pot-file with the --pot option and a list of po-files I'll
      remove from the po files those message translations of which the
      msgids are not in the pot-file and add messages that the pot-file has
      but the po-file doesn't.
      

  positional arguments:
    pofilename

  options:
    -h, --help            show this help message and exit
    --wrap                Wrap long lines.
    --no-wrap             Do not wrap long lines. This is the default.
    --width NUMBER        Set output page width. Default is 79.
    -p potfilename, --pot potfilename

filter
------

::

  usage: i18ndude filter [-h] [--wrap | --no-wrap] [--width NUMBER] file1 file2

      Given two pot-files I will write a copy of file1 to stdout with all
      messages removed that are also in file2, i.e. where msgids match.
      

  positional arguments:
    file1
    file2

  options:
    -h, --help      show this help message and exit
    --wrap          Wrap long lines.
    --no-wrap       Do not wrap long lines. This is the default.
    --width NUMBER  Set output page width. Default is 79.

admix
-----

::

  usage: i18ndude admix [-h] [--wrap | --no-wrap] [--width NUMBER] file1 file2

      Given two po-files I will look for translated entries in file2 that
      are untranslated in file1. I add these translations (msgstrs) to
      file1. Note that this will not affect the number of entries in file1.
      The result will be on stdout.
      

  positional arguments:
    file1
    file2

  options:
    -h, --help      show this help message and exit
    --wrap          Wrap long lines.
    --no-wrap       Do not wrap long lines. This is the default.
    --width NUMBER  Set output page width. Default is 79.

list
----

::

  usage: i18ndude list [-h] -p product [product ...] [-t] [--tiered]

      This will create a simple listing that displays how much of the
      combined products pot's is translated for each language. Run this
      from the directory containing the pot-files. The product name is
      normally a domain name.

      By default we show the languages of existing po files,
      ordered by percentage.

      With the --tiered option, we split the languages in three tiers or groups,
      the first two with languages that Plone was traditionally translated in,
      in a hardcoded order, followed by other languages.
      This was the default output for years.
      

  options:
    -h, --help            show this help message and exit
    -p product [product ...], --products product [product ...]
    -t, --table           Output as html table
    --tiered              Show in traditional three-tiered order

trmerge
-------

::

  usage: i18ndude trmerge [-h] [--wrap | --no-wrap] [--width NUMBER] [-i]
                          [--no-override]
                          file1 file2

      Given two po-files I will update all translations from file2 into
      file1. Missing translations are added.

      If a translation was fuzzy in file1, and there is a nonempty translation
      in file2, the fuzzy marker is removed.

      Fuzzy translations in file2 are ignored.

      The result will be on stdout.  If you want to update the first
      file in place, use a temporary file, something like this:

        i18ndude trmerge file1.po file2.po > tmp_merge && mv tmp_merge file1.po
      

  positional arguments:
    file1
    file2

  options:
    -h, --help          show this help message and exit
    --wrap              Wrap long lines.
    --no-wrap           Do not wrap long lines. This is the default.
    --width NUMBER      Set output page width. Default is 79.
    -i, --ignore-extra  Ignore extra messages: do not add msgids that are not in
                        the original po-file. Only update translations for
                        existing msgids.
    --no-override       Do not override translations, only add missing
                        translations.
