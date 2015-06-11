import imp
import os
import re
import unittest
from tempfile import NamedTemporaryFile
from jsonrpc2_zeromq import RPCServer, RPCClient

class MockGameRPCServer(RPCServer):
	def handle_report_stop_method(self, crashed):
		pass

	def handle_should_finish_method(self):
		return True

class BaseTestSandbox(unittest.TestCase):

	def setUp(self):
		self.endpoint = 'tcp://127.0.0.1:50000'
		self.server = MockGameRPCServer(timeout=.5, endpoint=self.endpoint)
		self.server.start()

	def tearDown(self):
		self.server.stop()
		self.server.join()
		del self.server

from spectrumwars.sandbox import ThreadedSandbox

class TestThreadedSandbox(BaseTestSandbox):

	def test_empty(self):
		sandbox = ThreadedSandbox([])
		players = sandbox.get_players()
		self.assertEqual(players, [])

	def test_simple(self):

		from spectrumwars import Transceiver

		class Receiver(Transceiver):
			pass

		class Transmitter(Transceiver):
			pass

		sandbox = ThreadedSandbox([[Receiver, Transmitter]])
		players = sandbox.get_players()

		self.assertEqual(len(players), 1)

		player = players[0]

		player.rx.init(player.i, 1.)
		player.tx.init(player.i, 1.)

		player.rx.start(self.endpoint)
		player.tx.start(self.endpoint)

		player.rx.join()
		player.tx.join()
