.. vim:sw=3 ts=3 expandtab tw=78

Testbed reference
=================

VESNA
-----

VESNA testbed uses VESNA sensor nodes with narrow-band radios as transceivers
in the 2.4 GHz band. An Ettus Research USRP N200 is used as a spectrum sensor.

Use ``-t vesna`` to with ``spectrumwars_runner`` to use this testbed.

=====================================  ===================
parameter                              value
=====================================  ===================
Maximum packet length	               252 bytes
Number of frequency channels           64
Number of bandwidth settings           4 (see :ref:`bw`)
Number of transmission power settings  17 (see :ref:`pow`)
=====================================  ===================

Central frequency of a channel can be calculated using the following formula::

      f = 2400.0 MHz + <chan> * 0.1 MHz


.. _bw:
.. table:: Interpretation of bandwidth settings

   =============  =======
   ``bandwidth``  bitrate
   =============  =======
   0              50 kbps
   1              100 kbps
   2              200 kbps
   3              400 kbps
   =============  =======


.. _pow:
.. table:: Interpretation of transmission power settings

   =========  =====
   ``power``  dBm
   =========  =====
   0          0
   1          -2
   2          -4
   3          -6
   4          -8
   5          -10
   6          -12
   7          -14
   8          -16
   9          -18
   10         -20
   11         -22
   12         -24
   13         -26
   14         -28
   15         -30
   16         < -55
   =========  =====

.. _sim-reference:

Simulated testbed
-----------------

Simulated testbed uses a software simulation to run the game. No special
hardware is required. This is useful when developing player code.

This testbed is used by default by ``spectrumwars_runner``, if no ``-t``
argument is specified.

Capabilities of this testbed can be customized using the following keyword
arguments (use ``-Okeyword=value`` in the ``spectrumwars_runner`` command-line
to modify their values from default):

===============  =====================================  =======  =====
keyword          meaning                                default  unit
===============  =====================================  =======  =====
packet_size      Maximum packet length	                 1024     bytes
frequency_range  Number of frequency channels           64
bandwidth_range  Number of bandwidth settings           10
power_range      Number of transmission power settings  10
send_delay       Time for sending one packet            0.100    s
===============  =====================================  =======  =====

Note that the simulation of the radio environment is greatly simplified:

 * A packet occupies only the channel it is sent on.

 * Sending of all packets takes the same amount of time (``send_delay``),
   regardless of ``bandwidth`` setting.

 * Only very simple collision detection is implemented. If transmission of
   two packets commences within the ``send_delay`` of each other, the first
   packet will be successfully delivered to its recepient, while the second
   will be discarded.

 * Spectrum sensing shows higher received power on channels with recent
   packet transmissions.

 * Transmission power setting is ignored.
