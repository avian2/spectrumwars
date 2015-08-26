.. vim:sw=3 ts=3 expandtab tw=78

Testbed-specific installation instructions
==========================================

VESNA
-----

VESNA testbed uses VESNA sensor nodes designed by the Institute Jožef Stefan.

Required hardware
^^^^^^^^^^^^^^^^^

* One USRP N200 connected over a gigabit Ethernet interface to be used as a
  spectrum sensor. Use default network settings (use 192.168.10.1 for the
  computer's IP)

  Current setup uses SBX daughterboard, a 2.4 GHz antenna.

* VESNA sensor nodes, connected through a powered USB hub. As many as you need
  (two nodes per player).

  Nodes should consist of a SNC core board and a SNE-ISMTV-2400 radio board.

  If you need to upload firmware, you will also need a SNE-PROTO board and a
  Olimex ARM-USB-OCD programmer. For debugging, a serial-to-USB converter
  connected to VESNA's USART1 is recommended.

.. note::
   As of 0.0.3, ``spectrumwars_runner`` no longer uses VESNA nodes connected
   over serial-to-USB converters.


Firmware compilation
^^^^^^^^^^^^^^^^^^^^

Firmware has to be uploaded to VESNA sensor nodes before they can be used with
Spectrum Wars. Firmware source code is stored in the ``firmware/`` subdirectory.

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

To test the firmware, connect two nodes using the mini-USB connector and run::

   $ cd ../controller
   $ python setup.py test -s tests.test_radio

.. note::
   In case of problems, there are some debugging options available on top of
   ``vsndriversconf.h``. See also :doc:`firmware`.


Additional dependencies for game controller
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In addition to packages listed in :doc:`install`, the following additional
packages are required to use Spectrum Wars game controller with the VESNA
testbed:

* GNU Radio with UHD (GNU Radio version 3.7.5.1 is known to work) - http://gnuradio.org
* gr-specest - https://github.com/avian2/gr-specest

* pyudev (``apt-get install python-pyudev``)
* pyserial (``pip install pyserial --user``)
