from setuptools import setup, find_packages
import sys, os

version = '3.0b2'

setup(name='i18ndude',
      version=version,
      description="i18ndude performs various tasks related to ZPT's, Python Scripts and i18n.",
      long_description="""i18ndude performs various tasks related to ZPT's, Python Scripts and i18n.""",
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Plone',
        'Framework :: Zope2',
        'Framework :: Zope3',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        ],
      keywords='Plone i18n zpt',
      author='Daniel Nouri',
      author_email='plone-i18n@lists.sourceforge.net',
      maintainer='Hanno Schlichting',
      maintainer_email='plone@hannosch.info',
      url='http://plone.org/products/i18ndude',
      license='GPL',
      package_dir = {'':'src'},
      packages=find_packages('src', exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      install_requires=['zope.tal >= 3.2',
                        'zope.interface >= 3.2',
                        'zope.i18nmessageid >= 3.2',
                        'zope.testing',
                        'elementtree'
      ],
      dependency_links=['http://download.zope.org/distribution/',],
      entry_points="""
      [console_scripts]
          i18ndude=i18ndude.script:main
      """,
      scripts=[],
      )
