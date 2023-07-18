from pathlib import Path
from setuptools import find_packages
from setuptools import setup


version = "6.1.0"

setup(
    name="i18ndude",
    version=version,
    description="i18ndude performs various tasks related to ZPT's, Python "
    "Scripts and i18n.",
    long_description=(
        Path("README.rst").read_text()
        + "\n\n"
        + (Path("docs") / "command.rst").read_text()
        + "\n\n"
        + Path("CHANGES.rst").read_text()
    ),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Utilities",
    ],
    keywords="Plone i18n zpt",
    author="Daniel Nouri",
    author_email="plone-i18n@lists.sourceforge.net",
    maintainer="Maurits van Rees",
    maintainer_email="maurits@vanrees.org",
    url="https://github.com/collective/i18ndude",
    license="GPL",
    package_dir={"": "src"},
    packages=find_packages(
        "src",
    ),
    include_package_data=True,
    zip_safe=False,
    test_suite="i18ndude.tests",
    python_requires=">=3.8",
    install_requires=[
        "lxml",
        "zope.i18nmessageid >= 3.3",
        "zope.interface >= 3.3",
        "zope.tal >= 4.3.0",
    ],
    extras_require={
        "plone": ["plone.i18n"],
    },
    entry_points={
        "console_scripts": [
            "i18ndude=i18ndude.script:main",
        ],
        # Documentation generation
        "zest.releaser.prereleaser.before": [
            "i18ndude_cli = i18ndude.utils:prepare_cli_documentation",
        ],
    },
)
