#!/usr/bin/env python

# distutils setup script:
# call it with: python setup.py install

from distutils.core import setup

setup(author='Plone I18N team',
      author_email='plone-i18n@lists.sourceforge.net',
      download_url='http://plone.org/products/i18ndude',
      description='i18ndude performs various tasks related to Zope '
      'products and i18n.',
      license='GPL',
      name='i18ndude',
      version=open('version.txt').read().strip(),
      package_dir = {'i18ndude':'.'},
      packages=['i18ndude'],
      scripts=['i18ndude'])
