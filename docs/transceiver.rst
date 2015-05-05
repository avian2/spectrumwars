.. vim:sw=3 ts=3 expandtab tw=78
Implementing a transceiver
==========================

.. py:class:: Transceiver

   You should provide two subclasses of the base ``Transceiver`` class:
   one for the transmitter and one for the receiver. Game controller makes one
   instance of the transmitter class and one instance of the receiver class.
   From the standpoint of the programming interface, the transmitter and
   receiver class are mostly identical (e.g. receiver can also send data to
   the transmitter). However in the game, their role differs: only payload
   data sent from the transmitter to the receiver counts towards the final
   score.

   You should override the following methods in the ``Transceiver`` class to
   create your transmitter and receiver classes. Do not override or use any
   members prefixed with an underscore (``_``). These are for internal use
   only.

   .. py:method:: start()

      Called by the game controller upon the start of the game. This method
      can perform any set-up required by the transceiver.

      By default, the method does nothing.

   .. py:method:: recv(data)

      Called by the game controller when the transceiver receives a packet
      (e.g. called on the receiver side when the transmitter side issued a
      send() and the packet was successfully received).

      Note that you do not need to override this method for the received
      payload to be counted towards your score. Overriding is only useful when
      you want to respond to a successfull reception of a packet or you want
      to do something with control data string sent by the transmitter.

      By default, the method does nothing.

   .. py:method:: status_update():

      Called by the game controller periodically with updates on the state of
      the game.

.. note::
   Blah

   The following methods are universal between transmitters and receivers:

   .. py:method:: set_configuration(frequency, power, bandwidth)

      Set up the transceiver for transmission or reception of packets on the
      specified central frequency, power and bandwidth.

   .. py:method:: get_configuration()

      Returns a ``(frequency, power, bandwidth)`` tuple containing the current
      transmission or reception configuration.

   .. py:method:: send(data=None)

      Send a data packet over the air. On the reception side, the ``recv()``
      method will be called upon the reception of the packet.

      ``data`` is an optional parameter that allows inclusion of an arbitrary
      control string into the packet. On the reception side, this string is
      passed as to the ``recv()`` method in the ``data`` parameter.

      Each testbed defines the maximum packet size ``packet_size`` (see
      ``get_packet_size()``).

      Upon successfull reception of the packet on the receiver side, ``n``
      bytes are counted towards the player's score, where ``n = packet_size -
      len(data)``.

   The following methods can be used to query the capabilities of the testbed.
   You can use them if your want to automatically adapt your algorithm to the
   testbed it is running on. If you are targeting just one testbed, you can
   ignore this part.

   .. py:method:: get_frequency_range()

   .. py:method:: get_power_range()

   .. py:method:: get_bandwidth_range()

   .. py:method:: get_packet_size()
