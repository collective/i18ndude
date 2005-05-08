#!/usr/bin/env python

# distutils setup script:
# call it with: python setup.py install

from distutils.core import setup

setup(author='Daniel Nouri',
      author_email='daniel.nouri@con-fuse.org',
      download_url='http://sourceforge.net/project/showfiles.php?'
      'group_id=66950&package_id=106648',
      description='i18ndude performs various tasks related to Zope Page '
      'Templates and i18n.',
      license='GPL',
      name='i18ndude',
      version=open('version.txt').read().strip(),
      package_dir = {'i18ndude':'.'},
      packages=['i18ndude'],
      scripts=['i18ndude'])
