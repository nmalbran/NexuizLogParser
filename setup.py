import os
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "NexuizLogParser",
    version = "1.0",
    author = "Nicolas Malbran",
    author_email = "nmalbran@gmail.com",

    description = "Log parser for Nexuiz game.",
    long_description=read('README.md'),
    keywords = "nexuiz log parser game",
    url = 'https://github.com/nmalbran/nexuiz-log-parser',
    download_url = 'https://github.com/nmalbran/nexuiz-log-parser',

    packages = find_packages(),
    package_data={'nexuiz_log_parser': ['html_templates/*']},

    zip_safe = False,

    entry_points = {
        'console_scripts': [
            'nexlogparser = nexuiz_log_parser.nex_parser:main',
            'nexcsvfullparse = nexuiz_log_parser.full_csv_render:main',
        ],
    },
)
