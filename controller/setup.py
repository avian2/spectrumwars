#!/usr/bin/python

from setuptools import setup

setup(name='spectrumwars',
    version='0.0.2',
    description='A programming game where players compete for radio bandwidth.',
    license='GPL3',
    author='Tomaz Solc',
    author_email='tomaz.solc@ijs.si',
    packages = [ 'spectrumwars', 'spectrumwars.testbed' ],
    entry_points = {
        'console_scripts': [
            'spectrumwars_runner = spectrumwars.runner:main',
            'spectrumwars_plot = spectrumwars.plotter:main',
	    'spectrumwars_sandbox = spectrumwars.sandbox:SubprocessSandboxInstance.run',
        ]
    },

    test_suite = 'tests',
)
