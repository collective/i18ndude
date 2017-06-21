Changelog
=========

4.2 (2017-06-21)
----------------

New:

- In ``find-untranslated``, do not report items that get replaced by Chameleon syntax.
  So ``<span>${view/test}</span>`` will no longer get flagged as missing a translation.
  (Note that you still *can* add ``i18n:translate`` if it makes sense,
  like Plone does for translating the dynamically calculated review state.)
  [Netroxen, maurits]

- Find untranslated attributes now also checks for 'placeholder' attributes on
  input tags.

4.1 (2016-12-02)
----------------

New:

- Allow use of regular expressions for --exclude parameter. For example,
  use ``*.py`` to exclude all python files. This doesn't break existing
  behavior.  Do remember to use quotes around the expression.
  [laulaz, maurits]


4.0.1 (2015-12-03)
------------------

Fixes:

- Fixed some reported line numbers in find-untranslated.
  Fixes issue #34.
  [maurits]


4.0.0 (2015-12-03)
------------------

New:

- Extract strings from zcml.
  Issue #28
  [maurits]

- No longer print two blank lines at the end of .po and .pot files.
  [maurits]

- In the find-untranslated command, first try to parse a template as
  xml, which is good for non-html files.  If that fails, try to parse
  it as html with a little help from the lxml HTMLPaser, which handles
  html5 code much better.  If that fails, use our trusty home grown
  ``common.prepare_xml`` function, which treats everything as old
  html.  Note that we still use ``xml.sax`` as the core parser here.
  Issue #15
  [maurits]

- Ignore hidden files in the find-untranslated command.
  Issue #29
  [maurits]

- Use lxml instead of xml.etree or elementtree for parsing
  GenericSetup xml files.
  [maurits]


3.4.5 (2015-11-05)
------------------

New:

- First try the original zope.tal parser.  Only when this fails we try
  our own parser/generator.
  [maurits]

- Support Chameleon unnamed attributes without crashing.  For example:
  ``tal:attributes="python:{'data-something': 'chameleon-only'}"``
  [maurits]

- Support chameleon attributes tal:switch and tal:case.
  Fixes issue #24.
  [ale-rt]


3.4.4 (2015-11-04)
------------------

Fixes:

- Check ``tal:condition`` correctly when it is in a ``tal:something`` tag.
  [maurits]

- In ``find-untranslated`` only ignore ``tal:condition="nothing"``,
  not other conditions.
  Fixes issue #16.
  [maurits]

- Improved the ``prepare_xml`` function.  This tries to work around
  templates that miss the usual boiler plate, like
  ``xmlns:i18n="http://xml.zope.org/namespaces/i18n"``.  But there
  were some silly errors in it.
  This refs issue #16.
  [maurits]


3.4.3 (2015-09-01)
------------------

- Fix ``nosummary`` option from ``find-untranslated``.
  It was reporting wrong information.
  [gforcada]


3.4.2 (2015-07-16)
------------------

- Fix encoding errors with wrapAndQuoteString.
  [thet]

- Pep8.
  [thet]


3.4.1 (2015-06-25)
------------------

- Releasing as Python wheel too.
  [maurits]

- Fixed wrapping when string contains newline.
  Issue #13
  [maurits]


3.4.0 (2014-11-27)
------------------

- Drop Python 2.6 support.  It may still work, but the tests only run
  on Python 2.7.  Note that it is fine to use one central i18ndude
  command for all your projects, no matter what Python version they
  are using.
  [janjaapdriessen, maurits]

- For the find-untranslated feature, add the possibility to mark a tag to be
  ignored by setting the "i18n:ignore" attribute on the tag. Also works for
  attributes with the "i18n:ignore-attributes" attribute.
  [janjaapdriessen]


3.3.5 (2014-08-05)
------------------

- Avoid AttributeError: 'NoneType' object has no attribute 'comments'
  when a ``.po`` file is missing an empty msgid and msgstr near the
  top.  This is fixed automatically, although it will override some
  headers.
  [maurits]


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
