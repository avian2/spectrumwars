.. vim:sw=3 ts=3 expandtab tw=78

Testbed reference
=================

VESNA
-----

VESNA testbed uses VESNA sensor nodes with narrow-band radios as transceivers
in the 2.4 GHz band. An Ettus Research USRP N200 is used as a spectrum sensor.

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

