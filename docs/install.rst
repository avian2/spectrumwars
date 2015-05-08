.. vim:sw=3 ts=3 expandtab tw=78

Installation instructions
=========================


Required hardware
-----------------

* One USRP N200 connected over a gigabit Ethernet interface to be used as a
  spectrum sensor. Use default network settings (use 192.168.10.1 for the
  computer's IP)

  Current setup uses SBX daughterboard, a 2.4 GHz antenna.

* VESNA sensor nodes, USART1 connected over USB-to-serial converters. As many as you
  need (two nodes per player).

  Nodes should consist of a SNC core board and a SNE-ISMTV-2400 radio board.

  If you need to upload firmware, you will also need a SNE-PROTO board and a
  Olimex ARM-USB-OCD programmer.


Firmware compilation
--------------------

Firmware is stored in the ``firmware/`` subdirectory.

You will need the ARM toolchain installed. See
https://sensorlab.github.io/vesna-manual/ for instructions. These steps assume
you are using Linux and that the command line tools are properly set up.

You will also need a checkout of the ``vesna-drivers`` repository. Current
packet driver in the ``master`` branch is very unstable and unsuitable to be
used with this firmware. It is recommended that you use the ``spectrumwars``
branch from the following repository:

https://github.com/avian2/vesna-drivers

First make sure that the ``VESNALIB_LOCATION`` in the ``Makefile`` points to
the directory containing the ``vesna-drivers`` git repository::

   $ cd firmware
   $ grep VESNALIB_LOCATION= Makefile

To compile the firmware run::

   $ make

To upload the firmware, make sure you have the Olimex ARM-USB-OCD connected to
the node and run::

   $ make install

To test the firmware, connect two nodes (``/dev/ttyUSB0`` and
``/dev/ttyUSB1``) using USB-to-serial converters and run::

   $ cd ../controller
   $ python setup.py test -s tests.test_radio

(Note that it might fail on the first pass)


Installing game controller
--------------------------

You need the following packages installed:

* GNURadio with UHD (version 4.7.2 is known to work) - http://gnuradio.org

* gr-specest - https://github.com/avian2/gr-specest

* numpy (``apt-get install python-numpy``)
* matplotlib (``apt-get install python-matplotlib``)

To install, run::

   $ cd controller
   $ python setup.py install --user

To run tests::

   $ python setup.py test

(note that some tests expect that you have a USRP and two nodes connected)

Building HTML documentation
---------------------------

To rebuild documentation run::

   $ cd docs
   $ make html

Index is in ``_build/html/index.html``



Requirements:

GNU Radio
gr-specest

