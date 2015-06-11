import imp
import os
import re
import time
import unittest
from tempfile import NamedTemporaryFile
from jsonrpc2_zeromq import RPCServer, RPCClient

class MockGameRPCServer(RPCServer):
	def handle_report_stop_method(self, crashed):
		self.crashed += crashed
		self.stopped += 1

	def handle_should_finish_method(self):
		return True

class BaseTestSandbox(unittest.TestCase):

	def setUp(self):
		self.endpoint = 'tcp://127.0.0.1:50000'
		self.server = MockGameRPCServer(timeout=.5, endpoint=self.endpoint)
		self.server.stopped = 0
		self.server.crashed = 0
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

		self.assertEqual(self.server.stopped, 2)
		self.assertEqual(self.server.crashed, 0)

from spectrumwars.sandbox import SubprocessSandbox

class TestSubprocessSandbox(BaseTestSandbox):
	def write_temp_py(self, code):
		f = NamedTemporaryFile(suffix='.py')
		f.write(code)
		f.flush()

		return f

	def test_simple(self):

		f = self.write_temp_py("""from spectrumwars import Transceiver

class Receiver(Transceiver):
	pass

class Transmitter(Transceiver):
	pass
""")

		sandbox = SubprocessSandbox([f.name])
		players = sandbox.get_players()

		self.assertEqual(len(players), 1)

		player = players[0]

		player.rx.init(player.i, 1.)
		player.tx.init(player.i, 1.)

		player.rx.start(self.endpoint)
		player.tx.start(self.endpoint)

		player.rx.join()
		player.tx.join()

		self.assertEqual(self.server.stopped, 2)
		self.assertEqual(self.server.crashed, 0)

	def test_simple(self):

		f = self.write_temp_py("""from spectrumwars import Transceiver

class Receiver(Transceiver):
	def start(self):
		while True:
			pass

class Transmitter(Transceiver):
	pass
""")

		sandbox = SubprocessSandbox([f.name])
		players = sandbox.get_players()

		self.assertEqual(len(players), 1)

		player = players[0]

		player.rx.init(player.i, 1.)
		player.tx.init(player.i, 1.)

		player.rx.start(self.endpoint)
		player.tx.start(self.endpoint)

		now = time.time()
		deadline = now + 1

		player.rx.join(deadline=deadline)
		player.tx.join(deadline=deadline)

		self.assertEqual(self.server.crashed, 1)
		self.assertEqual(self.server.stopped, 2)
