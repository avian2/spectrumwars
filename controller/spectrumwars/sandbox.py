import imp
import logging
import os
import re
import threading
from jsonrpc2_zeromq import RPCClient

from spectrumwars import Player

log = logging.getLogger(__name__)

class SandboxedPlayer(object):
	def __init__(self, rx, tx, i):
		self.rx = rx
		self.tx = tx
		self.i = i

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

			player = SandboxedPlayer(sbrx, sbtx, i)
			players.append(player)

		log.info("Loaded %d players" % (len(players),))

		return players
