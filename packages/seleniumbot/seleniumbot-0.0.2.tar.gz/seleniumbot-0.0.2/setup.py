from os import path

from setuptools import setup, find_packages

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='seleniumbot',
    version='0.0.2',
    packages=find_packages(),
    url='https://github.com/Mercurial5',
    author='Mercurial5',
    author_email='dias.nespayev@gmail.com',
    keywords='SeleniumBot',
    description='SeleniumBot',
    python_requires=">=3.11",
    install_requires=['selenium'],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
