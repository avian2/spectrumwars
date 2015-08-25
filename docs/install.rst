.. vim:sw=3 ts=3 expandtab tw=78

Installation instructions
=========================

Setting up the testbed
----------------------

If you would like to run Spectrum Wars on real hardware, you first have to
setup the testbed. Follow the instructions in the appropriate section of :doc:`installtestbed`.

Skip this step if you would only like to use Spectrum Wars with a simulated
testbed.


Installing game controller
--------------------------

You need the following packages installed:

* GNU Radio with UHD (GNU Radio version 3.7.5.1 is known to work) - http://gnuradio.org

* gr-specest - https://github.com/avian2/gr-specest

* jsonrpc2-zeromq (``pip install jsonrpc2-zeromq --user``)

* numpy (``apt-get install python-numpy``)
* matplotlib (``apt-get install python-matplotlib``)

* Sphinx (only required for building documentation; ``apt-get install python-sphinx``)

To install, run::

   $ cd controller
   $ python setup.py install --user

To run tests::

   $ python setup.py test

Note that to run the testbed-specific tests, you need to have the hardware
connected at this point.

.. note::
   If you get errors like ``SandboxError: Can't find 'spectrumwars_sandbox' in
   PATH``, check whether the scripts installed by ``setup.py`` are in your
   `PATH`. They are usually installed into ``$HOME/.local/bin`` if you used
   the ``--user`` flag as suggested above.

Building HTML documentation
---------------------------

To rebuild documentation run::

   $ cd docs
   $ make html

Index is in ``_build/html/index.html``
