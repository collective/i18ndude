i18ndude
========

.. contents::


Introduction
------------

i18ndude performs various tasks related to ZPT's, Python Scripts and i18n.

.. image:: https://github.com/collective/i18ndude/workflows/Tests/badge.svg
    :alt: GitHub Actions badge
    :target: https://github.com/collective/i18ndude/actions


Compatibility
-------------

i18ndude works with Python 3.8-3.11, and PyPy3.
Older versions are not supported anymore, use the i18ndude 5.x series
if you need that.

You can install ``i18ndude`` with Buildout or ``pip``.
With ``pip`` you may want to look at our `requirements.txt <https://github.com/collective/i18ndude/blob/master/requirements.txt>`_.

``UnicodeEncodeError``
----------------------

When running some ``i18ndude`` commands, you might get a ``UnicodeEncodeError``.
This can especially happen when ``i18ndude`` prints the result and you redirect the output or pipe it.
This is tricky, maybe impossible, to solve in ``i18ndude`` itself.
See this related `question on stackoverflow <https://stackoverflow.com/questions/492483/setting-the-correct-encoding-when-piping-stdout-in-python>`_.
This question points to a solution that you yourself can do when you encounter this.
In the (Unix-like) shell, do this::

    export PYTHONIOENCODING=utf-8

This fixes UnicodeEncodeErrors when piping or redirecting output that contains non-ascii.
I (Maurits) have this line in my bash profile now.

Note: if you get a ``UnicodeDecodeError``, so 'decode' instead of 'encode', then it may be something that needs fixing in ``i18ndude``.
Please `report <https://github.com/collective/i18ndude/issues>`_ it then.

Pre commit hook
---------------

Since version 6 we have a ``pre-commit`` hook available::

    -   repo: https://github.com/collective/i18ndude
        rev: "master"
        hooks:
        -   id: i18ndude

For now it only finds the strings not marked for translation.
