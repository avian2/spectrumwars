# Copyright (C) 2015 SensorLab, Jozef Stefan Institute http://sensorlab.ijs.si
#
# Written by Tomaz Solc, tomaz.solc@ijs.si
#
# This work has been partially funded by the European Community through the
# 7th Framework Programme project CREW (FP7-ICT-2009-258301).
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see http://www.gnu.org/licenses/

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
