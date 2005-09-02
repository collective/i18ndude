#!/usr/bin/env python

# distutils setup script:
# call it with: python setup.py install

from distutils.core import setup

setup(author='Daniel Nouri',
      author_email='daniel.nouri@con-fuse.org',
      download_url='http://plone.org/products/i18ndude',
      description='i18ndude performs various tasks related to Zope '
      'products and i18n.',
      license='GPL',
      name='i18ndude',
      version=open('version.txt').read().strip(),
      package_dir = {'i18ndude':'.'},
      packages=['i18ndude'],
      scripts=['i18ndude'])
