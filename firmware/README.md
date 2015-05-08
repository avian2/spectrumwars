This directory contains a firmware for nodes in the Spectrum Wars game.


Hardware
========

Firmware expects a SNC with SNE-ISMTV-2400.


Programming
===========

To program firmware using OpenOCD:

    $ make install

To run tests, connect two nodes to /dev/ttyUSB0 and /dev/ttyUSB1 and run

    $ python tests/tests.py


Usage
=====

Nodes use 115200 baud on the USART1 serial line. [Description of the protocol](https://docs.google.com/document/d/1DNTGHH97ehC-_zSoBDA6CvoCZiy6FznAtZA9by_ueaI/edit?pli=1).


Author
======

Tomaz Solc (tomaz.solc@ijs.si)
