i18ndude
========

.. contents::


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

If you add i18ndude to a buildout that handles a Zope, CMF or Plone
site, you probably already have versions pinned so then you do not
need to add an ``extends`` line.

You can also use ``pip`` or ``easy_install`` to install it.  With
``pip`` you may want to create a ``requirements.txt`` based on that
ztk versions list.
