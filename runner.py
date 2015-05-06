import imp
import logging
import os
import sys

from spectrumwars import Player, Game, GameController, Testbed

log = logging.getLogger(__name__)

def get_players(path):

	players = []

	n = 1
	while True:
		name = "player%d" % (n,)

		modpath = os.path.join(path, name + ".py")

		if not os.path.exists(modpath):
			break

		mod = imp.load_source(name, modpath)

		player = Player(mod.Receiver, mod.Transmitter)

		players.append(player)

		n += 1

	log.info("Loaded %d players" % (n-1,))

	return players

def main():
	PACKET_LIMIT = 50
	TIME_LIMIT = 10

	logging.basicConfig(level=logging.DEBUG)

	testbed = Testbed()
	players = get_players(sys.argv[1])

	game = Game(testbed, players, packet_limit=PACKET_LIMIT, time_limit=TIME_LIMIT)
	ctl = GameController()

	log.info("Running game...")

	results = ctl.run(game)

	log.info("Done.")

	print "Results:"
	for i, result in enumerate(results):

		ratio = 100. * result.received_packets / result.transmit_packets

		print "Player %d:" % (i+1,)
		print "    crashed: %s" % (result.crashed,)
		print "    transmit packets: %d" % (result.transmit_packets,)
		print "    received packets: %d (%.0f%%)" % (result.received_packets, ratio)

main()
