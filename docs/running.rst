.. vim:sw=3 ts=3 expandtab tw=78

Running player code
===================

To run a game with a single player that is specified by source code in
``examples/better_cognitive.py``::

   $ spectrumwars_runner -l example.log examples/better_cognitive.py

You can add more players to the game by specifying more Python files to the
command line.

.. note::
   By default ``spectrumwars_runner`` uses a simulated testbed that does not
   require any special hardware. If you have testbed-specific hardware
   installed, you can specify the testbed to use using the ``-t`` command line
   argument. For example, to run the game using the VESNA testbed, use::

      $ spectrumwars_runner -t vesna -l example.log examples/better_cognitive.py

   In this case, ``spectrumwars_runner`` automatically finds any USB-connected
   VESNA nodes and assigns them randomly to players.

   However, this is mostly intended for testbed developers. Playing
   SpectrumWars on a real testbed is usually done through a web interface.

While the game is running, you will see some debugging information on the
console. In the end, some game statistics are printed out::

   Results:
   Player 1:
       crashed             : False
       transmitted packets : 93
       received packets    : 51 (45% packet loss)
       transferred payload : 12801 bytes (avg 981.4 bytes/s)

   Game time: 13.0 seconds

If player code raised an unhandled exception at some point you will also see a
backtrace. This should assist you in debugging the problem.

``spectrumwars_runner`` allows you to set the game end conditions using the
command-line arguments.  Run ``spectrumwars_runner --help`` to see a list of
supported arguments with descriptions. Also note that the capabilities of the
``simulation`` testbed can be customized to more closely resemble one of the
real SpectrumWars testbeds. See :ref:`sim-reference`.

In addition to the ASCII log that is printed on the console, the game
controller also saves a binary log file to ``example.log``. The binary log
contains useful debugging information about events that occurred during the
game. You can visualize the log by running::

   $ spectrumwars_plot -o example.out example.log

This creates a directory ``example.out`` with a few images in it. One
visualization is created for each player participating in the game. These are
named ``player0.png``, ``player1.png`` and so on, using the same order as it
was used on the ``spectrumwars_runner`` command line. One additional
visualization named ``game.png`` is created showing the overall progress of
the game.

See :doc:`visualizations` on how to read the graphs produced by
`spectrumwars_plot`.
