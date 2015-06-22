.. vim:sw=3 ts=3 expandtab tw=78

Implementing a transceiver
==========================

You should provide two subclasses of the base ``Transceiver`` class:
one for the transmitter (named ``Transmitter``) and one for the receiver
(named ``Receiver``). Game controller makes one instance of the transmitter
class and one instance of the receiver class.  From the standpoint of the
programming interface, the transmitter and receiver class are mostly
identical (e.g. receiver can also send data to the transmitter). However in
the game, their role differs: only payload data sent from the transmitter
to the receiver counts towards the final score.

The ``Transceiver`` class interface has been designed to accomodate two
programming styles: procedural programming and event-based programming.

This is how a simple procedural receiver looks like::

   class Receiver(Transceiver):
      def start(self):
         # do some setup
         self.set_configuration(...)

         # loop until the game ends
         while True:
            # ask for the most recent spectrum scan and game status
            status = self.get_status()
            ...

            for packet in self.recv_loop():
               # do something with queued-up packet data
               ...

And this is how an identical event-based receiver looks like::

   class Receiver(Transceiver):
      def start(self):
         # do some setup
         self.set_configuration(...)

      def recv(self, packet):
         # do something with received packet data
         ...

      def status_update(self, status):
         # do something with the updated spectrum scan
         ...

Both styles are compatible and you can use a combination of both if you wish.
If you are unsure which one to use, we recommend the procedural style.

Class reference
---------------

.. py:class:: Transceiver

   You should override the following methods in the ``Transceiver`` class to
   create your transmitter and receiver classes. Do not override or use any
   members prefixed with an underscore (``_``). These are for internal use
   only.

   .. py:method:: start()

      Called by the game controller upon the start of the game. This method
      can perform any set-up required by the transceiver.

      Once this method returns, the game controller's event loop will start
      calling ``recv()`` and ``status_update()`` methods as corresponding
      events occur. You can however prevent this method from returning and use
      it to implement your own loop, as in the procedural example above. Of
      course, other players will not wait until your ``start()`` returns.

      If left unimplemented, this method does nothing.

   .. py:method:: recv(packet)

      Called by the game controller when the transceiver receives a packet
      (e.g. called on the receiver side when the transmitter side issued a
      send() and the packet was successfully received).

      Note that you do not need to override this method for the received
      payload to be counted towards your score. Overriding is only useful when
      you want to respond to a successfull reception of a packet or you want
      to do something with the data in the packet sent by the transmitter.

      ``packet`` is a ``RadioPacket`` object containing the string that was
      passed to ``send()`` on the transmitting side.

      If left unimplemented, this method does nothing.

   .. py:method:: status_update(status):

      Called by the game controller periodically with updates on the state of
      the game.

      ``status`` is a ``GameStatus`` object.

      If left unimplemented, this method does nothing.

   From these overriden methods you can call the following methods to control
   your transceiver:

   .. py:method:: set_configuration(frequency, bandwidth, power)

      Set up the transceiver for transmission or reception of packets on the
      specified central frequency, power and bandwidth.

      ``frequency`` is specified as channel number from 0 to N-1, where N is
      the value returned by the ``get_frequency_range()`` method. Central
      frequencies of channels are hardware dependent.
      
      ``bandwidth`` is specified as an integer specifying the radio bitrate
      and channel bandwidth in the interval from 0 to N-1, where N is the
      value returned by the ``get_bandwidth_range()`` method. Exact
      interpretation of this value is hardware dependent. Higher values always
      mean higher bitrates and wider channel bandwidths.

      ``power`` is specified as an integer specifying the transmission power
      in the interval from 0 to N-1, where N is the value returned by the
      ``get_power_range()`` method. Exact interpretation of this value is
      hardware dependent. Higher values always mean **lower** power.

      See :doc:`testbeds` for interpretations of these values.

      Invalid values will raise a ``RadioError`` exception.

      .. note::
         While specific meanings of these settings are hardware specific, you
         can assume that your receiver and transmitter will only be able to
         communicate successfully if both use the same ``frequency`` and
         ``bandwidth`` settings. The ``power`` setting is less critical, but
         higher power will usually lead to more reliable communication.

   .. py:method:: get_configuration()

      Returns a ``(frequency, bandwidth, power)`` tuple containing the current
      transmission or reception configuration.

   .. py:method:: send(data=None)

      Send a data packet over the air. On the reception side, the ``recv()``
      method will be called upon the reception of the packet.

      ``data`` is an optional parameter that allows inclusion of an arbitrary
      string into the packet. On the reception side, this string is passed to
      the ``recv()`` method in the ``data`` field of the ``RadioPacket``
      object.

      Note that the length is limited by the maximum packet size supported by
      the radio (as returned by ``get_packet_size()``). Longer strings will
      raise a ``RadioError`` exception.

      Upon successfull reception of the packet on the receiver side, ``n``
      bytes are counted towards the player's score, where ``n = packet_size -
      len(data)``.

   .. py:method:: get_status()

      Returns the current state of the game in a ``GameStatus`` object.

   .. py:method:: recv_loop(timeout=1.)

      Returns an iterator over the packets in the receive queue. Packets are
      returned as ``RadioPacket`` objects.

      ``timeout`` specifies the receive timeout. Iteration will stop if the
      queue is empty and no packets have been received for the specified
      number of seconds (note that floating point values < 1 are supported)

   The following methods can be used to query the capabilities of the testbed.
   You can use them if your want to automatically adapt your algorithm to the
   testbed it is running on. If you are targeting just one testbed, you can
   ignore this part and look at the :doc:`testbeds`.

   .. py:method:: get_frequency_range()

      Returns the number of available frequency channels.

   .. py:method:: get_bandwidth_range()

      Returns the number of available bandwidth settings.

   .. py:method:: get_power_range()

      Returns the number of available transmission power settings.

   .. py:method:: get_packet_size()

      Returns maximum number of bytes that can be passed to ``send()``.


.. py:class:: GameStatus

   The ``GameStatus`` class contains the current status of the game. The
   following attributes are defined:

   .. py:attribute:: spectrum

      This attribute contains the current state of the radio spectrum.

      ``spectrum`` is a list of floating point values. Each value is received
      power in a frequency channel in decibels, as seen at the antenna of the
      spectrum sensor observing the game. Frequency channels are the same as
      ones used by ``set_configuration()``. Length of the list is equal to the
      value returned by ``get_frequency_range()``. Reported power levels are
      relative.

      For example, if ``spectrum[10] == -60``, that means that -60 dB of power
      have been seen by the sensor on the radio channel obtained by
      ``set_configuration(10, x, y)``.

      .. note::

         ``send()`` radio transmissions typically occupy several radio
         channels around the specified central frequency specified by
         ``set_configuration()``. Number of occupied channels depends on the
         specified bitrate.

.. py:class:: RadioPacket

   A ``RadioPacket`` object is passed to the receiving transceiver for each
   successfully received packet. The following attributes are defined:

   .. py:attribute:: data

      This attribute contains the string that was passed to the ``send()``
      method on the transmitting side.
