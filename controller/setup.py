#!/usr/bin/python

from setuptools import setup

setup(name='spectrumwars',
    version='0.0.1',
    description='A programming game where players compete for radio bandwidth.',
    license='GPL3',
    author='Tomaz Solc',
    author_email='tomaz.solc@tablix.org',
    packages = [ 'spectrumwars', 'spectrumwars.testbed' ],
    entry_points = {
        'console_scripts': [
            'spectrumwars_runner = spectrumwars.runner:main'
        ]
    },

    test_suite = 'tests',
)
