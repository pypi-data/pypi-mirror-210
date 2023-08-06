from setuptools import setup, find_packages
import codecs
import os

_directory = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(_directory, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '1.1.2'
DESCRIPTION = 'Get the latest Cyber Security updates curated from different sources under one roof.'
LONG_DESCRIPTION = 'Python package and API that make use of Web-Scraping under the hood and provides a variety of curated news related to cyberspace from various sources under one roof. It is designed to help technology enthusiasts stay up-to-date with the latest updates in the field.'

"""
    Setting up
"""

setup(
    name="cybernews",
    version=VERSION,
    author="GhoulBond",
    author_email="hitesh22rana@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['beautifulsoup4', 'lxml', 'httpx', 'requests'],
    keywords=['python', 'web scraping', 'news', 'cyber news', 'hacker news', 'hacking',
              'cyber', 'free', 'open source', 'latest news', 'project', 'api', 'REST-API', 'cyber security', 'cybersecurity', 'updates', 'news', 'cyber attacks', 'cyber threats', 'online security'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
