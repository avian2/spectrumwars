import imp
import logging
import os
import re
import sys
import pickle
import argparse

from spectrumwars.sandbox import SubprocessSandbox
from spectrumwars import Player, Game, GameController
from spectrumwars.testbed.vesna import Testbed

log = logging.getLogger(__name__)

def run(args):
	logging.basicConfig(level=logging.DEBUG)
	logging.getLogger('jsonrpc2_zeromq').setLevel(logging.WARNING)

	testbed = Testbed()
	sandbox = SubprocessSandbox(args.player_paths)

	game = Game(testbed, sandbox, packet_limit=args.packet_limit, time_limit=args.time_limit)
	ctl = GameController()

	log.info("Running game...")

	results = ctl.run(game)

	log.info("Done.")

	print "Results:"
	for i, result in enumerate(results):

		ratio = 100. * result.received_packets / result.transmit_packets

		game_time = game.end_time - game.start_time

		print "Player %d:" % (i+1,)
		print "    crashed             : %s" % (result.crashed,)
		print "    transmitted packets : %d" % (result.transmit_packets,)
		print "    received packets    : %d (%.0f%%)" % (result.received_packets, ratio)
		print "    transferred payload : %d bytes (avg %.1f bytes/s)" % (
				result.payload_bytes, result.payload_bytes / game_time)
		print "Game time: %.1f seconds" % (game_time,)

	if args.log_path:
		pickle.dump(game.log, open(args.log_path, "wb"))

def main():
	parser = argparse.ArgumentParser(description="run a spectrum wars game")

	parser.add_argument('player_paths', metavar='PATH', nargs='+',
			help='path to .py file containing player classes')

	parser.add_argument('--time-limit', metavar='SECONDS', type=int, dest='time_limit', default=30,
			help='time limit for the game (default: 30 seconds)')
	parser.add_argument('--packet-limit', metavar='PACKETS', type=int, dest='packet_limit', default=50,
			help='number of packets required to win (default: 50)')

	parser.add_argument('-l', '--log', metavar='PATH', dest='log_path',
			help='path to save binary game log to')

	args = parser.parse_args()

	run(args)
