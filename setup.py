import os
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "nexuiz-log-parser",
    version = "0.1",
    packages = find_packages(exclude=['players.py']),
    author = "Nicolas Malbran",
    author_email = "nmalbran@gmail.com",
    description = "Log parser for Nexuiz game.",
    long_description=read('README.md'),

    keywords = "nexuiz log parser game",

    url = 'https://github.com/nmalbran/nexuiz-log-parser',

    zip_safe = False,

    entry_points = {
        'console_scripts': [
            'nexuizlogparser = nex_parser:main',
        ],
    },
)
