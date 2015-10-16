.. vim:sw=3 ts=3 expandtab tw=78

Installation instructions
=========================


Getting the source
------------------

Up-to-date development version is available on GitHub at:

https://github.com/avian2/spectrumwars

You can download the source using the following command::

   $ git clone https://github.com/avian2/spectrumwars.git

If you intend to do development, it's best if you make your own fork of the
repository on GitHub.

SpectrumWars releases are also `available from PyPi
<https://pypi.python.org/pypi/spectrumwars>`_.

Setting up the testbed
----------------------

If you would like to run Spectrum Wars on real hardware, you first have to
setup the testbed. Follow the instructions in the appropriate section of :doc:`installtestbed`.

Skip this step if you would only like to use Spectrum Wars with a simulated
testbed.


Installing game controller
--------------------------

You need the following packages installed:

* jsonrpc2-zeromq (``pip install jsonrpc2-zeromq --user``)

* numpy (``apt-get install python-numpy``)
* matplotlib (``apt-get install python-matplotlib``)

To install, run::

   $ cd controller
   $ python setup.py install --user

To run unit tests shipped with the code::

   $ python setup.py test

Note that to run the testbed-specific tests, you need to have the testbed
hardware connected and working at this point.

Tests that require hardware or optional external dependencies that were not
found on the system are skipped (check the console output for any lines that
say ``skip``).

.. note::
   If you get errors like ``SandboxError: Can't find 'spectrumwars_sandbox' in
   PATH``, check whether the scripts installed by ``setup.py`` are in your
   `PATH`. They are usually installed into ``$HOME/.local/bin`` if you used
   the ``--user`` flag as suggested above.

Building HTML documentation
---------------------------

You need the following software installed to build documentation:

* Sphinx (``apt-get install python-sphinx``)

To rebuild documentation run::

   $ cd docs
   $ make html

Index page is created at ``_build/html/index.html``.
