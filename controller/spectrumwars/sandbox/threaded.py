import threading
import time
from spectrumwars.rpc import RPCClient

from spectrumwars.sandbox import SandboxPlayer, SandboxBase, SandboxTransceiverBase

# ThreadedSandbox provides no isolation between the player's code and the game
# controller. It is mostly used for debugging and as an example of how the
# Sandbox interface works.

class ThreadedSandboxTransceiver(SandboxTransceiverBase):
	def __init__(self, cls, i, role):
		super(ThreadedSandboxTransceiver, self).__init__(i, role)
		self.cls = cls

	def init(self, update_interval):
		self.ins = self.cls(self.i, self.role, update_interval)

	def start(self, endpoint):
		client = RPCClient(endpoint)

		self.thread = threading.Thread(target=self.ins._start, args=(client,))
		self.thread.start()

	def join(self, deadline=None, timefunc=time.time):
		self.thread.join()

class ThreadedSandbox(SandboxBase):
	def __init__(self, cls_list):
		self.players = []

		for i, (dst_cls, src_cls) in enumerate(cls_list):
			player = SandboxPlayer(
				ThreadedSandboxTransceiver(dst_cls, i, 'dst'),
				ThreadedSandboxTransceiver(src_cls, i, 'src'), i)
			self.players.append(player)

	def get_players(self):
		return self.players
