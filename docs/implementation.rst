.. vim:sw=3 ts=3 expandtab tw=78

Implementation notes
====================

* USRP spectrum sensing is inspired by a real-time signal analyzer. e.g. we do
  continuous end-to-end FFTs with no blind time for all received samples. The
  spectral density is then averaged over a window of 200 ms. This is the main
  reason why sensing is very CPU intensive and we can't sense more than 64
  channels (even if USRP frontend bandwidth would allow for more).

  Sensing in this way is necessary because the radios have a very low duty
  cycle (e.g. a "while True: send()" has only around 10% duty cycle). If we
  would only take one sample the spectrum when players request it, it would
  mostly appear empty. Hence the need to take a moving average if sensing is to
  be useful for detecting transmissions.

* The corrolary of the above is that even 64 channels is a very generous
  portion of the spectrum for this game. A single channel could in theory
  accomodate 10 players with very little interferrence.

* Currently, it is very simple to cheat, since both of the player's transceiver
  classes exist in the same Python interpreter (in fact, in the same Python
  module). This makes it trivial to share state between the through global
  variables. In the future, these two classes should be isolated in separate
  processes and sand-boxed in some way.

* Similarly, there are very few protections against bugs in the player's code.
  It is trivial to create a player that makes the game run indefinitely, crash
  or worse. Current implementation is only a working demonstration of the class
  interface that is exposed to players.

* I believe that in the final user interface for this game, it is crucial that
  both console log of the running game and the visualized timeline are
  presented to each player. Without this kind of feedback it is very hard to
  develop a working algorith.

* There is no concept of radio power usage, battery level, etc. as discussed in
  the original design document. I believe these are unnecessary complications
  and in any case would only be simulated since radios always run on external
  power. If the aim is to encourage players to conserve power, this can be
  achieved with appropriate scoring function (e.g. give negative score for
  excessive number of transmitted packets or high transmission power)

* There is no scoring function defined at the moment.

* There is no backchannel communication between the player's classes
  implemented. I believe this is an unnecessary complication and current
  experience shows that it is quite simple to use data in the packet to
  communicate between the nodes. This is also a more realistic scenario.
