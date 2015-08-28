.. vim:sw=3 ts=3 expandtab tw=78

Introduction
============

SpectrumWars is a programming game where players compete for
bandwidth on a limited piece of a radio spectrum. Its aim is to show the
problems in spectrum sharing in an entertaining way. It captures the
competition between various groups of users. Such competition is increasingly
a factor in wireless communications as users demand more data in an even
increasing variety of situations.

SpectrumWars extends the concept developed by P. Sutton and L. Doyle in `The
gamification of Dynamic Spectrum Access & cognitive radio`_ by changing the
role of the human competitors. In the initial concept, competitors are
directly controlling transceivers via joystics. In this SpectrumWars
implementation, they instead develop an algorithm that controls the
transceivers in their place.

The competitive aspect of SpectrumWars was inspired in part by the `DARPA
Spectrum Challenge`_. However the goal here is to make the game as accessible
and as fun as possible. The trade-off between realism for simplicity is
heavily skewed towards the latter. For example, the interface between the
player's code and the transceiver is greatly simplified, limiting the number
of transceiver settings to just three: radio channel, bit rate and
transmission power. This kind of a simplified toy-like interface was inspired
by existing programming games, like the venerable `RobotWar` and its clones.

One aspect of real-life radio communications was not sacrified though:
SpectrumWars games run on real hardware and use real radiofrequency spectrum.
While a simulator is available to ease the development and debugging of player
code, the SpectrumWars challenge runs on hardware provided by partners of
the `CREW project`_ and takes place on real wireless testbeds.


Overview of the game
--------------------

Competitors develop their algorithms using the Python scripting language. In a
single game, two or more algorithms (`players`) compete with each other to
transfer some useful data from a transmitter to a receiver as quickly and as reliably
as possible. A good player for example will avoid interference from other
players and the environment.

Players are aided in this task with the help of a spectrum sensor. In the
game, the spectrum sensor is a centralized, simplified spectrum analyzer that
is always available to the players. An algorithm can query it to get an
up-to-date picture of the occupancy of the spectrum in the form of a power
spectral density function.

The nature of the data being transferred is not directly known to players - it
could conceivably be a machine-to-machine link sending sensor data, or it
could be someone on a coffee break browsing their favorite social networking
website. The player code only controls the connection and in fact does not
need to concern itself with the payload part of the packets it is sending over
the air.

Each player is given control of two transceivers (radio front-ends). For the
purpose of the game, payload only needs to go from one transceiver
(called `transmitter`) to the other one (called `receiver`). The players make
use of a simple interface that provides basic control over the radio.

The separation between the receiver and transmitter poses another challenge
the players must overcome. There is no reliable back channel to use for
synchronization between the two. A rendezvous strategy is therefore required
for all but the most simple algorithms.

Players are ranked by different statistics, like average packet loss and
throughput. Different challenges are possible within the basic SpectrumWars
framework. Some challenges might give more weight to the power efficiency of
the players, while others might favor resilience against interference. Some
might encourage players to intentionally interfere with competitors. Again
some others might introduce an interfering spectrum user to the testbed where
the game is played, but that is external to the game itself.

.. _The gamification of Dynamic Spectrum Access & cognitive radio: http://www.researchgate.net/profile/Paul_Sutton4/publication/261508380_The_Gamification_of_Dynamic_Spectrum_Access__Cognitive_Radio/links/00b495346b0140d996000000.pdf
.. _DARPA Spectrum Challenge: http://spectrum.ieee.org/telecom/wireless/radio-wrestlers-fight-it-out-at-the-darpa-spectrum-challenge
.. _RobotWar: https://en.wikipedia.org/wiki/RobotWar
.. _CREW Project: http://www.crew-project.eu/
