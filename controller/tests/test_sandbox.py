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

import imp
import logging
import os
import re
import time
import unittest
from tempfile import NamedTemporaryFile
from spectrumwars.rpc import RPCServer, RPCClient

level = logging.WARNING
logging.basicConfig(level=level)

class MockGameRPCServer(RPCServer):
	def handle_report_stop_method(self, crashed, crash_report=None):
		self.crashed += crashed
		if crashed:
			self.crash_report.append(crash_report)
		self.stopped += 1

	def handle_should_finish_method(self):
		return True

	def handle_get_ranges_method(self):
		return (0, 0, 0)

	def handle_recv_method(self, timeout):
		return None

class BaseTestSandbox(unittest.TestCase):

	def setUp(self):
		self.endpoint = 'tcp://127.0.0.1:50000'
		self.server = MockGameRPCServer(timeout=.5, endpoint=self.endpoint)
		self.server.stopped = 0
		self.server.crashed = 0
		self.server.crash_report = []
		self.server.start()

	def tearDown(self):
		self.server.stop()
		self.server.join()
		del self.server

from spectrumwars.sandbox.threaded import ThreadedSandbox

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

		player.dst.init(1.)
		player.src.init(1.)

		player.dst.start(self.endpoint)
		player.src.start(self.endpoint)

		player.dst.join()
		player.src.join()

		self.assertEqual(self.server.stopped, 2)
		self.assertEqual(self.server.crashed, 0)

from spectrumwars.sandbox.process import SubprocessSandbox

class TestSubprocessSandbox(BaseTestSandbox):
	def write_temp_py(self, code):
		f = NamedTemporaryFile(suffix='.py')
		f.write(code)
		f.flush()

		return f

	def run_players(self, players):
		for player in players:
			player.dst.init(1.)
			player.src.init(1.)

		for player in players:
			player.dst.start(self.endpoint)
			player.src.start(self.endpoint)

		for player in players:
			player.dst.join()
			player.src.join()

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

		self.run_players(players)

		self.assertEqual(self.server.stopped, 2)
		self.assertEqual(self.server.crashed, 0)

	def test_new_names(self):

		f = self.write_temp_py("""from spectrumwars import Transceiver

class Destination(Transceiver):
	pass

class Source(Transceiver):
	pass
""")

		sandbox = SubprocessSandbox([f.name])
		players = sandbox.get_players()

		self.assertEqual(len(players), 1)

		self.run_players(players)

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

		player.dst.init(1.)
		player.src.init(1.)

		player.dst.start(self.endpoint)
		player.src.start(self.endpoint)

		now = time.time()
		deadline = now + 1

		player.dst.join(deadline=deadline)
		player.src.join(deadline=deadline)

		self.assertEqual(self.server.crashed, 1)
		self.assertEqual(self.server.stopped, 2)
		self.assertEqual(len(self.server.crash_report), 1)
		self.assertTrue("Time" in self.server.crash_report[0])

	def _test_exception_on_import(self, code):
		f = self.write_temp_py(code)
		sandbox = SubprocessSandbox([f.name])
		players = sandbox.get_players()

		self.assertEqual(len(players), 1)

		self.run_players(players)

		self.assertEqual(self.server.crashed, 2)
		self.assertEqual(self.server.stopped, 2)
		self.assertEqual(len(self.server.crash_report), 2)
		self.assertTrue("Traceback" in self.server.crash_report[0])

	def test_syntax_error(self):
		self._test_exception_on_import('(')

	def test_name_error(self):
		self._test_exception_on_import('(')
