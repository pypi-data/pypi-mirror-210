# Always prefer setuptools over distutils
# To use a consistent encoding
from codecs import open
from os import path

import setuptools
from setuptools import setup

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="datatable_ajax_request_parser",
    version="1.0.0",
    description="Helper function to parse ajax datatable request into usable dictionary",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Yap ZhiHon",
    author_email="y.zhihon@gmail.com",
    classifiers=[
        "Operating System :: OS Independent"
    ],
    packages=setuptools.find_packages(
        include=['datatable_ajax_request_parser', 'datatable_ajax_request_parser.*']
    ),
    include_package_data=True,
    extras_require={
        "Django": ["Django>=4.2.1"],
    },
    python_requires='>=3.10',
)
