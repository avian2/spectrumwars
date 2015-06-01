import imp
import logging
import os
import re

from spectrumwars import Player

log = logging.getLogger(__name__)

class SandboxInstance(object):
	def __init__(self, transceiver):
		self.transceiver = transceiver

class Sandbox(object):
	def __init__(self, paths):
		self.paths = paths

	def get_players(self):
		players = []

		for path in self.paths:
			name = os.path.basename(path)
			name = re.sub("\.py$", "", name)

			mod = imp.load_source(name, path)

			sbrx = SandboxInstance(mod.Receiver)
			sbtx = SandboxInstance(mod.Transmitter)

			player = Player(sbrx, sbtx)
			players.append(player)

		log.info("Loaded %d players" % (len(players),))

		return players
