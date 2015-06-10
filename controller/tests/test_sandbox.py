import unittest
from tempfile import NamedTemporaryFile
from jsonrpc2_zeromq import RPCServer, RPCClient

from spectrumwars.sandbox import Sandbox

class MockGameRPCServer(RPCServer):
	def handle_report_stop_method(self, crashed):
		pass

	def handle_should_finish_method(self):
		return True

class TestSandbox(unittest.TestCase):

	def setUp(self):
		self.endpoint = 'tcp://127.0.0.1:50000'
		self.server = MockGameRPCServer(timeout=.5, endpoint=self.endpoint)
		self.server.start()

	def tearDown(self):
		self.server.stop()
		self.server.join()
		del self.server

	def test_empty(self):
		sandbox = Sandbox([])

		players = sandbox.get_players()

		self.assertEqual(players, [])


	def test_simple(self):
		f = NamedTemporaryFile(suffix='.py')
		f.write("""from spectrumwars import Transceiver

class Receiver(Transceiver):
	pass

class Transmitter(Transceiver):
	pass
""")
		f.flush()

		sandbox = Sandbox([f.name])

		players = sandbox.get_players()

		self.assertEqual(len(players), 1)

		player = players[0]

		player.rx.init(player.i, 1.)
		player.tx.init(player.i, 1.)

		player.rx.start(self.endpoint)
		player.tx.start(self.endpoint)

		player.rx.join()
		player.tx.join()
