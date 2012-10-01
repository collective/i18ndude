Changelog
=========

3.2.3 (unreleased)
------------------

- Moved code to https://github.com/collective/i18ndude
  [maurits]


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
