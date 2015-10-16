#!/usr/bin/python

import codecs
import os
from setuptools import setup

def read_doc(name):
	return codecs.open(os.path.join(os.path.dirname(__file__), name), encoding='utf8').read()

def get_long_description():
	return read_doc("README.rst")

setup(name='spectrumwars',
    version='0.0.6',
    description='A programming game where players compete for radio bandwidth.',
    license='GPL3',
    author='Tomaz Solc',
    author_email='tomaz.solc@ijs.si',
    url='https://github.com/avian2/spectrumwars',
    long_description=get_long_description(),
    packages = [ 'spectrumwars', 'spectrumwars.testbed', 'spectrumwars.sandbox' ],
    entry_points = {
        'console_scripts': [
            'spectrumwars_runner = spectrumwars.runner:main',
            'spectrumwars_plot = spectrumwars.plotter:main',
	    'spectrumwars_sandbox = spectrumwars.sandbox.process:SubprocessSandboxTransceiver.run',
        ]
    },

    test_loader = 'tests:Loader',
    test_suite = 'tests',

    install_requires = [ 'numpy', 'matplotlib', 'jsonrpc2-zeromq' ],

    classifiers = [
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
	"Topic :: Games/Entertainment :: Simulation",
	"Topic :: Scientific/Engineering",
    ],
)
