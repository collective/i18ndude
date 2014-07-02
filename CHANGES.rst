Changelog
=========

3.3.4 (2014-07-02)
------------------

- Wrap first line correctly.  Fixes #9.
  [gforcada]


3.3.3 (2013-11-27)
------------------

- Package housekeeping.
  [hvelarde]


3.3.2 (2013-11-27)
------------------

- ``trmerge``: do not override when the mixin translation is fuzzy.
  [maurits]

- ``trmerge``: add ``--no-override`` argument.  This means: do not
  override translations, only add missing translations.
  [maurits]

- ``trmerge``: add ``--ignore-extra`` option.  This ignores extra msgids
  in the second po-file.
  [maurits]


3.3.1 (2013-10-18)
------------------

- Update script.py in some cases "arguments.exclude" is None.
  [giacomos]

- Fixed optional parameter exclude.
  [shylux]


3.3.0 (2013-10-13)
------------------

- Add command line documentation to long description of package.
  [maurits]

- Add options ``--wrap``, ``--no-wrap`` and ``--width=NUMBER`` to all
  commands that write files.  Use these to determine whether long
  lines are wrapped and at which width.  Default width is 79.  By
  default we do NOT wrap, because we have never wrapped before.  This
  may change in the future, so if you *really* want to be sure to not
  wrap when using a future i18ndude version, you can add ``--no-wrap``
  now.
  https://github.com/collective/i18ndude/issues/3
  [maurits]

- Fix the ``list`` command to also work in a ``locales`` structure.
  [maurits]

- Fix an error in the ``merge`` command where the ``--merge`` option
  would be used as value for the ``--merge2`` option as well, if that
  option itself was unused.  This led to unneeded warnings.
  [maurits]

- The ``--create domain`` option of ``rebuild-pot`` is now optional.
  If not given, i18ndude reads the domain from the given ``.pot``
  file.  It was always optional, but the documentation did not show it
  and it did not work.
  [maurits]

- Update the command line options handling.  You can now get the help
  for individual commands by calling them with the ``--help`` option.
  [maurits]

- Return exit code 1 when the called function gives an error.  This
  currently only has an effect when calling ``find-untranslated``.
  https://github.com/collective/i18ndude/issues/1
  [maurits]

- Moved code to https://github.com/collective/i18ndude
  [maurits]

- Backslash escape added to msgid when it includes double quotes.
  [taito]

- Add trmerge command to merge po files. Custom tailored for transifex.
  [do3cc]


3.2.2 (2010-12-11)
------------------

- Encode key to utf-8 for the Merge-Warning message to avoid a
  UnicodeEncodeError.
  [mikerhodes]


3.2.1 (2010-10-31)
------------------

- Fixed making POT file for DOUBLE BYTE strings on default.
  [terapyon]


3.2 (2010-09-04)
----------------

- Replaced internal odict implementation by the ordereddict package.
  (implementation backported from Python 2.7)
  [vincentfretin]


3.1.3 (2010-09-04)
------------------

- Avoid UnicodeDecodeError when printing warning message in add().
  [rnix]


3.1.2 (2010-02-14)
------------------

- elementtree is only required for Python < 2.5.
  [vincentfretin]

- Fixed tests (patch provided by John Trammell).
  [vincentfretin]


3.1.1 (2009-11-22)
------------------

- Strip "src" only once in the pathname for the comments.
  Example: before it generated the following comment
  "#: archetypes.referencebrowserwidget/"
  which was not so useful. Now it generates
  "archetypes.referencebrowserwidget/src/archetypes/referencebrowserwidget/..."
  [vincentfretin]


3.1 (2009-10-31)
----------------

- Support for explicit msgids in GSReader.
  [vincentfretin]

- Better handling of msgid references. Keep all the references in PTReader
  and PYReader. In POWriter, normalize and sort the references, write only
  MAX_OCCUR (default is 3) references.
  You can set MAX_OCCUR=None if you want all references to be written to
  the generated POT file. Only the first reference is written in case of
  several references to the same file but with different line number.
  [vincentfretin]

- Depend now on zope.tal 3.5.2 to print a warning when msgid already exists
  in catalog with a different default message. Simplified PTReader code.
  Check for msgid with different default in GSReader, PYReader and in the
  merged catalog (ptctl, pyctl, gsctl).
  [vincentfretin]

- Fix behaviour when dealing with broken xml files to be parsed.
  [afd]


3.0 (2008-11-13)
----------------

- No changes.
  [hannosch]


For older changes, see ``docs/ChangeLog``.
