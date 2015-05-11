.. vim:sw=3 ts=3 expandtab tw=78

Implementation notes
====================

* Currently, it is very simple to cheat, since both of the player's transceiver
  classes exist in the same Python interpreter (in fact, in the same Python
  module). This makes it trivial to share state between the through global
  variables. In the future, these two classes should be isolated in separate
  processes and sand-boxed in some way.

* Similarly, there are very few protections against bugs in the player's code.
  It is trivial to create a player that makes the game run indefinitely, crash
  or worse. Current implementation is only a working demonstration of the class
  interface that is exposed to players.

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
