import logging
import numpy as np

from spectrumwars.rpc import RPCServer, RPCClient
from spectrumwars.transceiver import Transceiver, StopGame

import unittest

level = logging.WARNING
logging.basicConfig(level=level)

class MockGameRPCServer(RPCServer):
	def handle_report_stop_method(self, crashed, crash_report=None):
		pass

	def handle_should_finish_method(self):
		return False

	def handle_get_ranges_method(self):
		return (10, 10, 10)

	def handle_set_configuration_method(self, frequency, bandwidth, power):
		pass

	def handle_recv_method(self, timeout):
		pass

class MockTransceiver(Transceiver):
	def start(self):
		raise StopGame

class TestTransceiver(unittest.TestCase):

	def setUp(self):
		endpoint = 'tcp://127.0.0.1:50000'

		self.server = MockGameRPCServer(timeout=.5, endpoint=endpoint)
		self.server.start()

		self.client = RPCClient(endpoint)

	def tearDown(self):
		self.server.stop()
		del self.server

	def test_numpy_int32(self):
		t = MockTransceiver(0, 'rx', 1.)
		t._start(self.client)
		t.set_configuration(np.int32(0), np.int32(0), np.int32(0))

	def test_numpy_int64(self):
		t = MockTransceiver(0, 'rx', 1.)
		t._start(self.client)
		t.set_configuration(np.int64(0), np.int64(0), np.int64(0))

	def test_numpy_float32(self):
		t = MockTransceiver(0, 'rx', .1)
		t._start(self.client)

		for packet in t.recv_loop(timeout=np.float32(.1)):
			pass

	def test_numpy_float64(self):
		t = MockTransceiver(0, 'rx', .1)
		t._start(self.client)

		for packet in t.recv_loop(timeout=np.float64(.1)):
			pass
