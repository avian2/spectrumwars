import logging
import unittest
from jsonrpc2_zeromq import RPCClient

from spectrumwars import Player, Game, GameController, Transceiver, RadioError
from spectrumwars.testbed.vesna import Testbed, list_radio_devices
from spectrumwars.sandbox import ThreadedSandbox

level = logging.WARNING
logging.basicConfig(level=level)

class TestVESNAGame(unittest.TestCase):

	PACKET_LIMIT = 1
	TIME_LIMIT = 1

	def setUp(self):
		self.testbed = Testbed()

		if len(list_radio_devices()) < 2:
			raise unittest.SkipTest("less than two VESNA nodes connected")

	def _run_game(self, rxcls, txcls):
		sandbox = ThreadedSandbox([[rxcls, txcls]])
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
