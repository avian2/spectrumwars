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

from spectrumwars import Player, Game, GameController, Transceiver, RadioTimeout, RadioError
from spectrumwars.testbed.simulation import Testbed
from spectrumwars.sandbox.threaded import ThreadedSandbox

level = logging.WARNING
logging.basicConfig(level=level)

class TestSimulation(unittest.TestCase):

	def setUp(self):
		self.t = Testbed()
		self.r1, self.r2 = self.t.get_radio_pair()
		self.r3, self.r4 = self.t.get_radio_pair()

	def test_send(self):
		self.r1.set_configuration(0, 0, 0)
		self.r2.set_configuration(0, 0, 0)

		self.r1.send("foo", True)
		d = self.r2.recv(.1)

		self.assertEqual(d.data, "foo")

	def test_send_self(self):
		self.r1.set_configuration(0, 0, 0)

		self.r1.send("foo", True)
		self.assertRaises(RadioTimeout, self.r1.recv, .1)

	def test_send_invalid(self):
		self.r1.set_configuration(0, 0, 0)
		self.r2.set_configuration(1, 0, 0)

		self.r1.send("foo", True)
		self.assertRaises(RadioTimeout, self.r2.recv, .1)

	def test_send_invalid_2(self):
		self.r1.set_configuration(0, 0, 0)
		self.r2.set_configuration(0, 1, 0)

		self.r1.send("foo", True)
		self.assertRaises(RadioTimeout, self.r2.recv, .1)

	def test_power_ignored(self):
		self.r1.set_configuration(0, 0, 0)
		self.r2.set_configuration(0, 0, 1)

		self.r1.send("foo", True)
		self.assertEqual(self.r2.recv().data, "foo")

	def test_get_spectrum(self):
		s = self.t.get_spectrum()

		self.assertEqual(len(s), self.t.get_frequency_range())

	def test_simultaneous(self):
		self.r1.set_configuration(0, 0, 0)
		self.r2.set_configuration(0, 0, 0)

		self.r3.set_configuration(10, 0, 0)
		self.r4.set_configuration(10, 0, 0)

		sd = self.r1.send_delay
		self.r1.send_delay = 0
		self.r3.send_delay = 0

		self.r1.send("foo", True)
		self.r3.send("bar", True)

		self.assertEqual(self.r2.recv().data, "foo")
		self.assertEqual(self.r4.recv().data, "bar")

		self.r1.send_delay = sd
		self.r3.send_delay = sd

	def test_collision(self):
		self.r1.set_configuration(0, 0, 0)
		self.r2.set_configuration(0, 0, 0)

		self.r3.set_configuration(0, 0, 0)
		self.r4.set_configuration(0, 0, 0)

		sd = self.r1.send_delay
		self.r1.send_delay = 0
		self.r3.send_delay = 0

		self.r1.send("foo", True)
		self.r3.send("bar", True)

		self.assertEqual(self.r2.recv().data, "foo")
		self.assertRaises(RadioTimeout, self.r4.recv, .1)

		self.r1.send_delay = sd
		self.r3.send_delay = sd

	def test_get_packet_size(self):
		t = Testbed(packet_size=100)
		self.assertEqual(self.t.get_packet_size(), 100)


class TestSimulationGame(unittest.TestCase):

	PACKET_LIMIT = 1
	TIME_LIMIT = 1

	def setUp(self):
		self.testbed = Testbed()

	def _run_game(self, dst_cls, src_cls):
		sandbox = ThreadedSandbox([[dst_cls, src_cls]])
		game = Game(self.testbed, sandbox,
				packet_limit=self.PACKET_LIMIT, time_limit=self.TIME_LIMIT)
		ctl = GameController()
		return ctl.run(game)[0]

	def test_send_recv(self):

		cnt = [0]

		class Receiver(Transceiver):
			def recv(self, packet):
				cnt[0] += 1

		class Transmitter(Transceiver):
			def start(self):
				self.send()

		result = self._run_game(Receiver, Transmitter)
		self.assertEqual(cnt[0], 1)
