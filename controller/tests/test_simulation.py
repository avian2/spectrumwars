import logging
import unittest

from spectrumwars import Player, Game, GameController, Transceiver, RadioTimeout, RadioError
from spectrumwars.testbed.simulation import Testbed
from spectrumwars.sandbox import ThreadedSandbox

level = logging.WARNING
logging.basicConfig(level=level)

class TestSimulation(unittest.TestCase):

	def setUp(self):
		self.t = Testbed()
		self.r1, self.r2 = self.t.get_radio_pair()

	def test_send(self):
		self.r1.set_configuration(0, 0, 0)
		self.r2.set_configuration(0, 0, 0)

		self.r1.send("foo")
		d = self.r2.recv()

		self.assertEqual(d.data, "foo")

	def test_send_self(self):
		self.r1.set_configuration(0, 0, 0)

		self.r1.send("foo")
		self.assertRaises(RadioTimeout, self.r1.recv)

	def test_send_invalid(self):
		self.r1.set_configuration(0, 0, 0)
		self.r2.set_configuration(1, 0, 0)

		self.r1.send("foo")
		self.assertRaises(RadioTimeout, self.r2.recv)

	def test_get_spectrum(self):
		s = self.t.get_spectrum()

		self.assertEqual(len(s), self.t.get_frequency_range())

class TestSimulationGame(unittest.TestCase):

	PACKET_LIMIT = 1
	TIME_LIMIT = 1

	def setUp(self):
		self.testbed = Testbed()

	def _run_game(self, rxcls, txcls):
		sandbox = ThreadedSandbox([[rxcls, txcls]])
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
