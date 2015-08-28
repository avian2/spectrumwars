import threading
import time
from spectrumwars.rpc import RPCClient

from spectrumwars.sandbox import SandboxPlayer, SandboxBase, SandboxInstanceBase

# ThreadedSandbox provides no isolation between the player's code and the game
# controller. It is mostly used for debugging and as an example of how the
# Sandbox interface works.

class ThreadedSandboxInstance(SandboxInstanceBase):
	def __init__(self, cls, role):
		self.cls = cls
		self.role = role

	def init(self, i, update_interval):
		self.ins = self.cls(i, self.role, update_interval)

	def start(self, endpoint):
		client = RPCClient(endpoint)

		self.thread = threading.Thread(target=self.ins._start, args=(client,))
		self.thread.start()

	def join(self, deadline=None, timefunc=time.time):
		self.thread.join()

class ThreadedSandbox(SandboxBase):
	def __init__(self, cls_list):
		self.players = []

		for i, (rxcls, txcls) in enumerate(cls_list):
			player = SandboxPlayer(
				ThreadedSandboxInstance(rxcls, 'rx'),
				ThreadedSandboxInstance(txcls, 'tx'), i)
			self.players.append(player)

	def get_players(self):
		return self.players
