from setuptools import setup, find_packages
import sys, os

version = '2.1'

setup(name='i18ndude',
      version=version,
      description="i18ndude performs various tasks related to ZPT's, Python Scripts and i18n.",
      long_description="""\
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='Plone i18n zpt',
      author='Plone i18n team',
      author_email='plone-i18n@lists.sourceforge.net',
      url='http://plone.org/products/i18ndude',
      license='GPL',
      package_dir = {'i18ndude':'.'},
      packages=['i18ndude'],
      #packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      scripts=['i18ndude'],
      )
