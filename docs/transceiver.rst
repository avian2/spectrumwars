.. vim:sw=3 ts=3 expandtab tw=78
Implementing a transceiver
==========================

.. py:class:: Transceiver

   The following methods are universal between transmitters and receivers:

   .. py:method:: set_configuration(frequency, power, bandwidth)

      Set up the transceiver for transmission or reception of packets on the
      specified central frequency, power and bandwidth.

   .. py:method:: get_configuration()

      Returns a ``(frequency, power, bandwidth)`` tuple containing the current
      transmission or reception configuration.

   .. py:method:: send()

      Send a packet.

   The following methods should be overriden. Do not override any class
   members prefixed with an underscore (``_``).

   .. py:method:: start()

      Called by the game controller upon the start of the game. This method
      can perform any set-up required by the transceiver. By default does
      nothing.

   .. py:method:: recv()

      Called by the game controller upon reception of a packet. Required only
      for the receiver. By default does nothing.

   .. py:method:: status_update():

      Called by the game controller periodically with updates on the state of
      the game.

   The following methods can be used to query the capabilities of the testbed.
   You can use them if your want to automatically adapt your algorithm to the
   testbed it is running on. If you are targeting just one testbed, you can
   ignore this part.

   .. py:method:: get_frequency_range()

   .. py:method:: get_power_range()

   .. py:method:: get_bandwidth_range()
