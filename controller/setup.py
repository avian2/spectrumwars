#!/usr/bin/python

from setuptools import setup

setup(name='spectrumwars',
    version='0.0.4',
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

    test_loader = 'tests:Loader',
    test_suite = 'tests',

    install_requires = [ 'numpy', 'matplotlib', 'jsonrpc2-zeromq' ],
)
