#!/usr/bin/python

from setuptools import setup

setup(name='spectrumwars',
    version='0.0.1',
    description='A programming game where players compete for radio bandwidth.',
    license='GPL3',
    author='Tomaz Solc',
    author_email='tomaz.solc@tablix.org',
    packages = [ 'spectrumwars' ],
    test_suite = 'tests',
)
