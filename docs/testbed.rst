.. vim:sw=3 ts=3 expandtab tw=78

Adding support for a new testbed
================================

To add support for a new testbed, the following tasks need to be done:

Add testbed specific code blocks
   Add a module with the name like ``spectrumwars.testbed.xxx``. This module should
   define two classes: 
   
   * ``Testbed``, a subclass of ``TestbedBase``, and
   * ``Radio``, a subclass of ``RadioBase``.

Add testbed specific unit tests
   Add tests to a Python file with the name like ``tests/test_xxx.py``. Please
   make the tests automatically skip themselves if the testbed-specific
   hardware is not connected (e.g. raise the ``unittest.SkipTest`` exception)

Add testbed documentation
   Add testbed documentation for players to ``docs/reference.rst``. Add any
   testbed-specific installation instructions to ``docs/installtestbed.rst``.


Class reference
---------------

.. py:class:: Testbed

   ``Testbed`` objects represent a physical testbed that is used to run a
   game. Unless stated otherwise, subclasses should override all of the
   methods described below.

   The class constructor can take optional string-typed keyword arguments.
   These can be specified in ``spectrumwars_runner`` using the ``-O``
   arguments.

   .. py:method:: get_radio_pair()

      Returns a ``rxradio, txradio`` tuple. ``rxradio`` and ``txradio`` should
      be instances of a subclass of :py:class:`Radio`.

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
      :py:meth:`Radio.send` method.

      Corresponds to :py:meth:`Transceiver.get_packet_size`.

   .. py:method:: get_spectrum()

      Returns the current state of the radio spectrum as a list of floating
      point values.

      The value returned by this method gets assigned to
      :py:attr:`GameStatus.spectrum`.

      See also :py:class:`usrp_sensing.SpectrumSensor`.

   .. py:method:: time()

      Returns the current testbed time in seconds since epoch as a floating
      point number. Selection of an epoch does not matter. Game controller
      requires only that time increases monotonically.

      By default it returns ``time.time()``, which should be sufficient for
      most testbeds.

.. py:class:: Radio

   ``Radio`` objects represent a player's interface to a single
   transceiver. Unless stated otherwise, subclasses should override all of the
   methods described below.

   .. py:method:: set_configuration(frequency, bandwidth, power)

      Set up the transceiver for transmission or reception of packets on the
      specified central frequency, power and bandwidth.

      ``frequency`` is specified as channel number from 0 to N-1, where N is
      the value returned by the :py:meth:`Testbed.get_frequency_range()`
      method.

      ``bandwidth`` is specified as an integer specifying the radio bitrate
      and channel bandwidth in the interval from 0 to N-1, where N is the
      value returned by the :py:meth:`Testbed.get_bandwidth_range()` method.
      Higher values mean higher bitrates and wider channel bandwidths.

      ``power`` is specified as an integer specifying the transmission power
      in the interval from 0 to N-1, where N is the value returned by the
      :py:meth:`Testbed.get_power_range()` method. Higher values mean
      **lower** power.

      Corresponds to :py:meth:`Transceiver.set_configuration`.

   .. py:method:: send(data)

      Send a data packet over the air.
      
      ``data`` is a string with the optional control data to be included into
      the packet, or ``None``. Length of ``data`` can be up to ``PACKET_SIZE``,
      where ``PACKET_SIZE`` is the value returned by
      :py:meth:`Transceiver.get_packet_size`.

      Note that the game's scoring expects that all packets sent over the air
      have the same length and that any length unused by the control data is
      used by packet payload. It is up to the testbed to decide how this is
      implemented.

      For example, the ``send()`` method can pack the ``data`` string into a
      fixed-length packet like this::

         ------------------------------------------> bytes

         +-----+-----+     +-----+-----+     +-----+
         |  0  |  1  | ... |  n  | n+1 | ... |  m  |
         +-----+-----+     +-----+-----+     +-----+

            ^   <---- data -----> <---- payload --->
            |
            |

            len(data)


         n = len(data)

         m = PACKET_SIZE + 1

      Payload is discarded on reception and can be filled with random bytes.

      Corresponds to :py:meth:`Transceiver.send`.

   .. py:method:: recv(timeout=None)

      Return a packet from the receive queue.

      ``timeout`` specifies the receive timeout in seconds. If no packet is
      received within the timeout interval, the method raises ``RadioTimeout``
      exception.

      Upon successfull reception, the method should return an instance of
      :py:class:`RadioPacket`. This method should revert the control data
      packing performed by ``send()``. The content of the ``RadioPacket.data``
      property should be equal to the ``data`` parameter that was passed to
      the corresponding ``send()`` call.

      .. note::

         There is no way for the ``Radio`` class to push packets towards
         the game controller. Instead, the game controller polls the radio for
         received packets by calling ``recv()`` method, as instructed by
         player's code. Hence it is in most cases necessary that the actual
         packet reception happens in another thread (started typically from
         :py:meth:`Testbed.start`) and that the received packets are held
         in a queue until the next ``recv()`` call.

      Corresponds to :py:meth:`Transceiver.recv`.

.. py:class:: usrp_sensing.SpectrumSensor(base_hz, step_hz, nchannels, time_window=200e-3, gain=10)

   ``usrp_sensing.SpectrumSensor`` is a simple, reusable spectrum sensor
   implementation using a USRP device.

   The sensing algorithm is inspired by a real-time signal analyzer. The
   recorded samples are converted into power spectral density using continuous
   end-to-end FFTs with no blind time (and no overlap of the FFT windows). The
   spectral power density is then averaged over a time window.

   The algorithm is very CPU intensive. Using a 2.7 GHz CPU, it will be able to
   sense at most 64 channels (even if USRP frontend bandwidth would allow for
   more).

   Sensing in this way is necessary because the radios usually have a very low duty
   cycle (e.g. a "while True: send()" has only around 10% duty cycle on the
   VESNA testbed). If we would only take one sample the spectrum when players
   request it, it would mostly appear empty. Hence the need to take a moving
   average if sensing is to be useful for detecting player transmissions.

   `base_hz` is the lower bound of the frequency band used in the game in
   hertz. `step_hz` is the width of each channel. `nchannels` is the number of
   channels used in the game. The values for these parameters should be chosen
   so that the channel frequencies correspond to the channels used by the
   testbed's ``Radio`` class::

      -------------------------------> frequency (Hz)

      +---+---+     +---+
      | 0 | 1 | ... | n | (channels used in the game)
      +---+---+     +---+

      |---| <- step_hz

      |-----------------| <- step_hz * nchannels

      ^
      |

      base_hz


   `time_window` defines the length of the moving average filter in seconds.
   The value depends on how often players can look up the current state of the
   spectrum. In most cases it should be longer than the period of
   :py:meth:`Transceiver.status_update` events in the event-based model.

   .. py:method:: start()

      Start the worker thread. Should be called before first call to
      :py:meth:`get_spectrum`

   .. py:method:: stop()

      Stop the worker thread.

   .. py:method:: get_spectrum()

      Returns the current state of the radio spectrum as a list of floating
      point values. Length of the list is equal to `nchannels`.

      The value returned by this method can be directly used as the return value of
      :py:meth:`Testbed.get_spectrum`.
