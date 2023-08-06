# Always prefer setuptools over distutils
from setuptools import setup

# To use a consistent encoding
from codecs import open
from os import path

# Get the long description from the README file
HERE = path.abspath(path.dirname(__file__))
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='multi_stock_api',
    version='0.1.0',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Emir Moćević',
    author_email='emirmocevic88@gmail.com',
    license='MIT',
    packages=['multi_stock_api'],
    include_package_data=True
)