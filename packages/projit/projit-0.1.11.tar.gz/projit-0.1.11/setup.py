# -*- coding: utf-8 -*-
 
"""setup.py: setuptools control."""

import re
from setuptools import setup

version = re.search(
        '^__version__\s*=\s*"(.*)"',
        open('projit/__init__.py').read(),
        re.M
    ).group(1) 

with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")

# read the contents of your README file
#from pathlib import Path
#this_directory = Path(__file__).parent
#long_descr = (this_directory / "README.md").read_text()

setup(
    name = "projit",
    packages = ["projit"],
    license = "MIT",
    install_requires = ['numpy', 'pyyaml', 'pandas', 'fpdf', 'gitpython'],
    entry_points = {
        "console_scripts": ['projit = projit.cli:main']
    },
    include_package_data=True,
    version = version,
    description = "Python library and CLI for de-coupled data science project integration and management.",
    long_description=long_descr,
    long_description_content_type='text/markdown',
    author = "John Hawkins",
    author_email = "john@getting-data-science-done.com",
    url = "http://john-hawkins.github.io",
    project_urls = {
        'Documentation': "https://projit.readthedocs.io",
        'Source': "https://github.com/john-hawkins/projit",
        'Tracker': "https://github.com/john-hawkins/projit/issues" 
      }
    )

