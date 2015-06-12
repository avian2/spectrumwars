import imp
import logging
import os
import re
import time
import unittest
from tempfile import NamedTemporaryFile
from jsonrpc2_zeromq import RPCServer, RPCClient

level = logging.WARNING
logging.basicConfig(level=level)

class MockGameRPCServer(RPCServer):
	def handle_report_stop_method(self, crashed, crash_desc=None):
		self.crashed += crashed
		if crashed:
			self.crash_desc.append(crash_desc)
		self.stopped += 1

	def handle_should_finish_method(self):
		return True

class BaseTestSandbox(unittest.TestCase):

	def setUp(self):
		self.endpoint = 'tcp://127.0.0.1:50000'
		self.server = MockGameRPCServer(timeout=.5, endpoint=self.endpoint)
		self.server.stopped = 0
		self.server.crashed = 0
		self.server.crash_desc = []
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

	def test_loop(self):

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
		self.assertEqual(len(self.server.crash_desc), 1)
		self.assertTrue("Time" in self.server.crash_desc[0])

	def test_syntax(self):

		f = self.write_temp_py("(")
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

		self.assertEqual(self.server.crashed, 2)
		self.assertEqual(self.server.stopped, 2)
		self.assertEqual(len(self.server.crash_desc), 2)
		self.assertTrue("SyntaxError" in self.server.crash_desc[0])
