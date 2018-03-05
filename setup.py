import os
import sys

from setuptools import setup, find_packages

version = '5.0.0'

install_requires = [
    'lxml',
    'zope.i18nmessageid >= 3.3',
    'zope.interface >= 3.3',
    'zope.tal >= 4.3.0',
]

setup(
    name='i18ndude',
    version=version,
    description="i18ndude performs various tasks related to ZPT's, Python "
                "Scripts and i18n.",
    long_description=(open("README.rst").read() + "\n" +
                      open(os.path.join("docs", "command.rst")).read() + "\n" +
                      open("CHANGES.rst").read()),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Plone',
        'Framework :: Zope2',
        'Framework :: Zope3',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Framework :: Zope3',
        'Topic :: Utilities',
    ],
    keywords='Plone i18n zpt',
    author='Daniel Nouri',
    author_email='plone-i18n@lists.sourceforge.net',
    maintainer='Vincent Fretin',
    maintainer_email='vincent.fretin@gmail.com',
    url='https://github.com/collective/i18ndude',
    license='GPL',
    package_dir={'': 'src'},
    packages=find_packages('src', exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    test_suite='i18ndude.tests',
    install_requires=install_requires,
    extras_require={
        'plone': ['plone.i18n'],
    },
    entry_points={
        'console_scripts': [
            'i18ndude=i18ndude.script:main',
        ],
        # Documentation generation
        'zest.releaser.prereleaser.before': [
            'i18ndude_cli = i18ndude.utils:prepare_cli_documentation',
        ],
    },
)
