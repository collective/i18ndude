from setuptools import setup, find_packages
import os, sys

version = '3.1.2'
      
install_requires = [
  'zope.tal >= 3.5.2',
  'zope.interface >= 3.3',
  'zope.i18nmessageid >= 3.3',
  'plone.i18n',
]

if sys.version_info < (2, 5):
    install_requires.append('elementtree')

setup(name='i18ndude',
      version=version,
      description="i18ndude performs various tasks related to ZPT's, Python Scripts and i18n.",
      long_description=open("README.txt").read() + "\n" + \
                       open(os.path.join("docs", "HISTORY.txt")).read(),
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
      maintainer_email='hannosch@plone.org',
      url='http://pypi.python.org/pypi/i18ndude',
      license='GPL',
      package_dir={'': 'src'},
      packages=find_packages('src', exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points="""
      [console_scripts]
      i18ndude=i18ndude.script:main
      """,
      )
