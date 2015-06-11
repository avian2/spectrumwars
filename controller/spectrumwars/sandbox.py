import imp
import logging
import os
import re
import threading
from jsonrpc2_zeromq import RPCClient

from spectrumwars import Player

log = logging.getLogger(__name__)

class SandboxPlayer(object):
	def __init__(self, rx, tx, i):
		self.rx = rx
		self.tx = tx
		self.i = i

# ThreadedSandbox provides no isolation between the player's code and the game
# controller. It is mostly used for debugging and as an example of how the
# Sandbox interface works.

class ThreadedSandboxInstance(object):
	def __init__(self, cls, role):
		self.cls = cls
		self.role = role

	def init(self, i, update_interval):
		self.ins = self.cls(i, self.role, update_interval)

	def start(self, endpoint):
		client = RPCClient(endpoint)

		self.thread = threading.Thread(target=self.ins._start, args=(client,))
		self.thread.start()

	def join(self):
		self.thread.join()

class ThreadedSandbox(object):
	def __init__(self, cls_list):
		self.players = []

		for i, (rxcls, txcls) in enumerate(cls_list):
			player = SandboxPlayer(
				ThreadedSandboxInstance(rxcls, 'rx'),
				ThreadedSandboxInstance(txcls, 'tx'), i)
			self.players.append(player)

	def get_players(self):
		return self.players

class Sandbox(object):
	def __init__(self, paths):
		self.paths = paths

	def get_players(self):
		players = []

		for i, path in enumerate(self.paths):
			name = os.path.basename(path)
			name = re.sub("\.py$", "", name)

			mod = imp.load_source(name, path)

			sbrx = ThreadedSandboxInstance(mod.Receiver, 'rx')
			sbtx = ThreadedSandboxInstance(mod.Transmitter, 'tx')

			player = SandboxPlayer(sbrx, sbtx, i)
			players.append(player)

		log.info("Loaded %d players" % (len(players),))

		return players
