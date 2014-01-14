i18ndude
========

.. contents::


Introduction
------------

i18ndude performs various tasks related to ZPT's, Python Scripts and i18n.

.. image:: https://secure.travis-ci.org/collective/i18ndude.png?branch=master
    :alt: Travis CI badge
    :target: http://travis-ci.org/collective/i18ndude

Compatibility
-------------

i18ndude works with Python 2.6 and 2.7.  It is expected to work with
Python 2.4 and 2.5 too, but it may be tricky to get the proper
versions of its dependencies that work with those Python versions.

i18ndude uses a few zope packages.  If you install i18ndude using a
buildout, you may want to pin their versions to the ones in the
current latest ztk (Zope Tool Kit) versions, as that is what we test
with:
http://download.zope.org/zopetoolkit/index/1.1.6/ztk-versions.cfg

If you use a separate buildout for i18ndude, you may want to update
the ``zope.tal`` version to 4.0.0 or higher, with fixes a possible
UnicodeDecodeError while printing a warning when a msgid already
exists.  If you happen to hit that corner case, the new version should
help.

If you add i18ndude to a buildout that handles a Zope, CMF or Plone
site, you probably already have versions pinned so then you do not
need to add an ``extends`` line.

You can also use ``pip`` or ``easy_install`` to install it.  With
``pip`` you may want to create a ``requirements.txt`` based on that
ztk versions list.
