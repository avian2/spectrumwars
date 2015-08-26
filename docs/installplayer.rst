.. vim:sw=3 ts=3 expandtab tw=78

Installing the simulator
========================

The ``pip install`` command bellow will automatically install all missing
Python packages. However, installing some larger dependencies from scratch
can be a time consuming and error-prone process. It is therefore recommended
that you install some of them using your Linux distribution package manager.
Specifically:

 * `numpy` (run ``sudo apt-get install python-numpy`` on Debian-based systems)
 * `matplotlib` (run ``sudo apt-get install python-matplotlib`` on Debian-based
   systems)

To install the game controller, run::

   $ pip install spectrumwars --user

To check if the installation was successful, try running the game controller::

   $ spectrumwars_runner --help

If you get ``command not found`` error, check whether the scripts installed by
``pip`` are in your `PATH`. They are usually installed into
``$HOME/.local/bin``.
