import logging
import unittest
from jsonrpc2_zeromq import RPCClient

from spectrumwars import Player, Game, GameController, Transceiver
from spectrumwars.testbed.vesna import Testbed
from spectrumwars.sandbox import SandboxedPlayer

level = logging.WARNING
logging.basicConfig(level=level)

class MockSandboxedTransceiver(object):
	def __init__(self, cls, role):
		self.cls = cls
		self.role = role

	def init(self, i, update_interval):
		self.ins = self.cls(i, self.role, update_interval)

	def start(self, endpoint):
		client = RPCClient(endpoint)
		self.ins._start(client)

	def join(self):
		self.ins._join()

class MockSandbox(object):
	def __init__(self, rxcls, txcls):
		self.player = SandboxedPlayer(
				MockSandboxedTransceiver(rxcls, 'rx'),
				MockSandboxedTransceiver(txcls, 'tx'), 0)

	def get_players(self):
		return [self.player]

class TestVESNAGame(unittest.TestCase):

	PACKET_LIMIT = 1
	TIME_LIMIT = 1

	def setUp(self):
		self.testbed = Testbed()

	def _run_game(self, rxcls, txcls):
		sandbox = MockSandbox(rxcls, txcls)
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
