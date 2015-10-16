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

import logging
import unittest

from spectrumwars import Player, Game, GameController, Transceiver, RadioError
from spectrumwars.testbed.vesna import Testbed, list_radio_devices
from spectrumwars.sandbox.threaded import ThreadedSandbox

level = logging.WARNING
logging.basicConfig(level=level)

class TestVESNAGame(unittest.TestCase):

	PACKET_LIMIT = 1
	TIME_LIMIT = 1

	def setUp(self):
		self.testbed = Testbed()

		if len(list_radio_devices()) < 2:
			raise unittest.SkipTest("less than two VESNA nodes connected")

	def _run_game(self, dst_cls, src_cls):
		sandbox = ThreadedSandbox([[dst_cls, src_cls]])
		game = Game(self.testbed, sandbox,
				packet_limit=self.PACKET_LIMIT, time_limit=self.TIME_LIMIT)
		ctl = GameController()
		return ctl.run(game)[0]

	def test_max_length_packet_data(self):

		cnt = [0]
		foo = "x" * self.testbed.get_packet_size()

		class Receiver(Transceiver):
			def recv(self, packet):
				cnt[0] = packet

		class Transmitter(Transceiver):
			def start(self):
				self.send(foo)

		result = self._run_game(Receiver, Transmitter)
		self.assertEqual(cnt[0].data, foo)
		self.assertEqual(result.payload_bytes, 0)

	def test_config_error(self):

		cnt = [0]

		class Receiver(Transceiver):
			def start(self):
				try:
					self.set_configuration(self.get_frequency_range(), 0, 0)
				except RadioError:
					cnt[0] += 1

		result = self._run_game(Receiver, Transceiver)

		self.assertEqual(cnt[0], 1)
		self.assertFalse(result.crashed)
