from setuptools import setup, find_packages
import sys, os

version = '2.1'

setup(name='i18ndude',
      version=version,
      description="i18ndude performs various tasks related to ZPT's, Python Scripts and i18n.",
      long_description="""i18ndude performs various tasks related to ZPT's, Python Scripts and i18n.""",
      classifiers=[
          'Classifier: Development Status :: 5 - Production/Stable',
          'Classifier: Environment :: Console',
          'Framework :: Zope2',
          'Framework :: Zope3',
          'Classifier: License :: OSI Approved :: GNU General Public License (GPL)',
          'Classifier: Operating System :: OS Independent',
          'Classifier: Programming Language :: Python',
          'Classifier: Topic :: Utilities',
          ],
      keywords='Plone i18n zpt',
      author='Daniel Nouri',
      author_email='plone-i18n@lists.sourceforge.net',
      maintainer='Hanno Schlichting',
      maintainer_email='plone@hannosch.info',
      url='http://plone.org/products/i18ndude',
      license='GPL',
      package_dir = {'':'src'},
      #packages=find_packages(exclude=['ez_setup']),
      packages=['i18ndude'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      scripts=['src/i18ndude/i18ndude'],
      )
