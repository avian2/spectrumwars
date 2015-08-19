import imp
import importlib
import logging
import os
import re
import sys
import pickle
import argparse

from spectrumwars.sandbox import SubprocessSandbox
from spectrumwars import Player, Game, GameController

log = logging.getLogger(__name__)

def get_testbed_kwargs(options):
	kwargs = {}
	if options:
		for option in options:
			f = option.split('=', 1)
			if len(f) != 2:
				log.error("Invalid testbed option %r: should be in key=value format" %
						(option,))
				continue

			key, value = f
			kwargs[key] = value

	return kwargs

def get_testbed(name, options):
	mod = importlib.import_module("spectrumwars.testbed." + name)

	kwargs = get_testbed_kwargs(options)
	return mod.Testbed(**kwargs)

def run(args):
	logging.basicConfig(level=logging.DEBUG)
	logging.getLogger('jsonrpc2_zeromq').setLevel(logging.WARNING)

	testbed = get_testbed(args.testbed, args.testbed_options)
	sandbox = SubprocessSandbox(args.player_paths)

	game = Game(testbed, sandbox, packet_limit=args.packet_limit, time_limit=args.time_limit)
	ctl = GameController()

	log.info("Running game...")

	results = ctl.run(game)

	log.info("Done.")

	game_time = game.end_time - game.start_time

	print "Results:"
	for i, result in enumerate(results):

		if result.transmit_packets > 0:
			packet_loss = 100. * (result.transmit_packets - result.received_packets) / result.transmit_packets
			packet_loss_str = "(%.0f%% packet loss)" % (packet_loss,)
		else:
			packet_loss_str = ""

		print "Player %d:" % (i+1,)
		print "    crashed             : %s" % (result.crashed,)
		print "    transmitted packets : %d" % (result.transmit_packets,)
		print "    received packets    : %d" % (result.received_packets,), packet_loss_str
		print "    transferred payload : %d bytes (avg %.1f bytes/s)" % (
				result.payload_bytes, result.payload_bytes / game_time)
		print
		if result.crashed:
			print "   Crash reports:"
			for desc in result.crash_report:
				print desc
			print

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

	parser.add_argument('-t', '--testbed', metavar='TESTBED', dest='testbed', default='simulation',
			help='testbed to use (default: simulation)')

	parser.add_argument('-O', '--testbed-option', metavar='KEY=VALUE', nargs='*', dest='testbed_options',
			help='testbed options')

	args = parser.parse_args()

	run(args)
