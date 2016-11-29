from setuptools import setup
from setuptools import find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()

setup(
    name = 'ldrpremisbuilding',
    description = "A set of functions for adding to premis records in the livePremis environment.",
    long_description = readme(),
    version = '0.0.1dev',
    author = "Brian Balsamo, Tyler Danstrom",
    author_email = "balsamo@uchicago.edu, tdanstrom@uchicago.edu",
    packages = ['ldrpremisbuilding'],
    keywords = [
        "uchicago",
        "repository",
        "file-level",
        "premis",
        "utility"
    ],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Operating System :: Unix",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    dependency_links = [
        'https://github.com/uchicago-library/uchicagoldr-toolsuite' +
        '/tarball/master#egg=uchicagoldrtoolsuite',
        'https://github.com/uchicago-library/uchicagoldr-premiswork' +
        '/tarball/master#egg=pypremis',
    ],
)
