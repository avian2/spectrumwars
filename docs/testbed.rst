.. vim:sw=3 ts=3 expandtab tw=78

Adding support for a new testbed
================================

A testbed should subclass ``TestbedBase`` and ``RadioBase``.


Class reference
---------------

.. py:class:: TestbedBase

   ``TestbedBase`` objects represent a physical testbed that is used to run a
   game. Unless stated otherwise, subclasses should override all of the
   methods described below.

   .. py:method:: get_radio_pair()

      Returns a ``rxradio, txradio`` tuple. ``rxradio`` and ``txradio`` should
      be instances of a subclass of :py:class:`RadioBase`.

      This method is called multiple times by the game controller, once for
      each player to obtain the interfaces to player's radios. It is called
      before the game starts, and before the call to :py:meth:`start()`.

   .. py:method:: start()

      Called once, immediately before the start of the game.

   .. py:method:: stop()

      Called after the game concluded. This method should perform any clean-up
      tasks required by the testbed (e.g. stopping any threads started by
      :py:meth:`start()`.

   .. py:method:: get_frequency_range()

      Returns the number of frequency channels available to player's code. The
      value returned should not change during the lifetime of the object.

      Corresponds to :py:meth:`Transceiver.get_frequency_range`.

   .. py:method:: get_bandwidth_range()

      Returns the number of bandwidth settings available to player's code. The
      value returned should not change during the lifetime of the object.

      Corresponds to :py:meth:`Transceiver.get_bandwidth_range`.

   .. py:method:: get_power_range()

      Returns the number of transmission power settings available to player's
      code. The value returned should not change during the lifetime of the object.

      Corresponds to :py:meth:`Transceiver.get_power_range`.

   .. py:method:: get_packet_size()

      Returns the maximum length of a string that can be passed to the
      :py:meth:`RadioBase.send` method.

      Corresponds to :py:meth:`Transceiver.get_packet_size`.

   .. py:method:: get_spectrum()

      Returns the current state of the radio spectrum as a list of floating
      point values.

      The value returned by this method gets assigned to :py:attr:`GameStatus.spectrum`.

   .. py:method:: time()

      Returns the current testbed time in seconds since epoch as a floating
      point number. Selection of an epoch does not matter. Game controller
      requires only that time increases monotonically.

      By default it returns ``time.time()``, which should be sufficient for
      most testbeds.


.. py:class:: RadioBase

   ``RadioBase`` objects represent a player's interface to a single
   transceiver. Unless stated otherwise, subclasses should override all of the
   methods described below.

   .. py:method:: start()

      Called once immediately after the start of the game (e.g. after
      :py:meth:`TestbedBase.start` has been called, but before any other
      methods are called).

   .. py:method:: stop()

   .. py:method:: set_configuration(frequency, power, bandwidth)

   .. py:method:: send(data)

   .. py:method:: recv(timeout=None)

