.. vim:sw=3 ts=3 expandtab tw=78

An annotated example
====================

The ``examples`` directory in the SpectrumWars source tree contains a number
of player code examples (`see it on GitHub
<https://github.com/avian2/spectrumwars/tree/master/examples>`_). You are
encouraged to explore the example code and study how it works.  To help you,
``better_cognitive.py``, one of the examples, is explained step-by-step in
this section.

Refer to the :ref:`transceiver-reference` for details on SpectrumWars-specific
method calls used. The examples also use `numpy` to simplify some parts of the
code. See `NumPy reference
<https://docs.scipy.org/doc/numpy/reference/index.html>`_ for details.

::

   # Import the Transceiver base class.
   from spectrumwars import Transceiver

   # Also import NumPy to get some convenient array functions.
   import numpy as np

   # Two modules from the Python standard library we'll use.
   import random
   import time

   # First, let's write the code that controls our source.
   class Source(Transceiver):

      # We use the procedural style in this example, so we only override the
      # start() method. This way our code gets called right at the start of
      # the game. Our source will not leave this method until the game
      # ends.
      def start(self):

         # We simply make an infinite loop. We don't need to care what happens
         # when the game ends - game controller takes care of cleaning up
         # after us.
         while True:

            # Ignore this delay for now. Real testbeds have various delays
            # when sending packets or when sensing the spectrum. Sometimes it
            # helps to artificially slow down your algorithm.
            time.sleep(.2)

            # self.get_status().spectrum returns a list of received signal
            # strength indicators (RSSI) for all channels in the testbed.
            # Index into this array directly translates to the radio channel
            # number.
            #
            # We convert the result to a NumPy array for convenience.
            spectrum = np.array( self.get_status().spectrum )

            # These two lines take the RSSI list and select one channel at
            # random from 20 channels that have the lowest signal strength.
            chl = np.argsort(spectrum)
            ch = chl[random.randint(0, 20)]

            # Now we tune the radio to the selected channel. We also select
            # the slowest (and most reliable) bitrate setting and the
            # strongest transmission power.
            self.set_configuration(ch, 0, 0)

            # Next, we transmit 20 packets on the selected channel. We don't
            # add any control data to the packets, so the complete packet is
            # filled with payload by the game controller.
            for n in xrange(20):
               self.send()

               # We delay a little bit the transmission of packets.
               time.sleep(.05)

            # After 20 packets have been transmitted, our loop rolls around
            # for another iteration. We again check the spectrum occupancy,
            # select one of the channels that appear to be least occupied and
            # transmit another 20 packets.
            #
            # The spectrum sensor has some averaging. If we would loop
            # immediately from self.send() to self.get_status(), the spectral
            # scan would still contain the trace of our own packets. Hence the
            # 200 ms delay at the start of the loop to let our packets fall
            # out of the averaging window and make it possible to select the
            # same channel again.


   # Now for the destination side of the code.
   class Destination(Transceiver):

      # Again, destination spends the duration of the game in the start() method.
      def start(self):

         # Since the first thing we do in the source is a 200 ms delay,
         # there is no point in trying to receive anything earlier than that.
         time.sleep(.2)

         # Another infinite loop.
         while True:

            # Wait a bit more to be sure that the source is transmitting
            # at this point and that its packets have been picket up by the
            # spectrum sensor.
            time.sleep(.1)

            # Use the same method as in the source to get a NumPy array
            # containing RSSI values for all channels.
            spectrum = np.array( self.get_status().spectrum )

            # This line uses a similar argsort trick as in the source.
            # We want an array of channel numbers, sorted with the channel with
            # the highest signal strength on top.
            chl = np.argsort(spectrum)[::-1]

            # For each channel of the top five by signal strength...
            for ch in chl[:5]:

               # ... tune the radio to that channel. Set bitrate to the same
               # one as used by the source.
               #
               # We also set the transmit power to the higher setting. However
               # we don't transmit anything from the destination side in this
               # example.
               self.set_configuration(ch, 0, 0)

               # On the selected channel, wait 200 ms for a packet.
               for packet in self.recv_loop(timeout=.2):

                  # We don't do anything with the received packet - the
                  # source did not include any control data that would be
                  # interesting to us.
                  #
                  # Game controller takes care of the payload data automatically.
                  #
                  # If a packet has been received within 200 ms, the inner for
                  # loop rolls around and waits 200 ms for another packet.
                  pass

               # If a packet has not been received for 200 ms, the outer for
               # loop tries with the next most occupied channel.

            # If reception has been unsuccessful, the while loop rolls around
            # and performs another spectral scan, repeating the process.

At this point, you should try running this example in the simulation a few
times and check the resulting time-frequency diagrams. Try to run it in a game
competing with some other example players. Find its flaws and see how it can be
improved.
