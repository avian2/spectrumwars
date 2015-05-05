import imp
import os
import sys

from spectrumwars import Player, Game, GameController, Testbed

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

	print "Loaded %d players" % (n-1,)

	return players

def main():
	PACKET_LIMIT = 50
	TIME_LIMIT = 50

	testbed = Testbed()
	players = get_players(sys.argv[1])

	game = Game(testbed, players, packet_limit=PACKET_LIMIT, time_limit=TIME_LIMIT)
	ctl = GameController()

	print "Running game..."

	results = ctl.run(game)

	print "Done."
	print "Results:"

	for i, result in enumerate(results):
		print "Player %d:" % (i+1,)
		print "    packets: %d" % (result.packets)

main()
