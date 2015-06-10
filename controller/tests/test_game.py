import logging
import unittest

import Queue
from spectrumwars import Transceiver, Player, Game, GameController, RadioTimeout
from spectrumwars.testbed import TestbedBase, RadioBase, RadioPacket

level = logging.WARNING
logging.basicConfig(level=level)

def log_exc_off():
	logging.getLogger().setLevel(logging.ERROR)

def log_exc_on():
	logging.getLogger().setLevel(level)


class MockTestbed(TestbedBase):
	def get_radio_pair(self):

		rxradio = MockRadio(self)
		txradio = MockRadio(self)

		rxradio.neighbor = txradio
		txradio.neighbor = rxradio

		self.clock = 0.

		return rxradio, txradio

	def time(self):
		return self.clock

	def get_spectrum(self):
		return True

	def get_packet_size(self):
		return 200

class MockRadio(RadioBase):
	def __init__(self, testbed):
		self.testbed = testbed
		self.neighbor = None

		self.settings = None
		self.rx_queue = Queue.Queue()

	def send(self, data):
		if self.settings == self.neighbor.settings:
			self.neighbor.rx_queue.put(data)

	def set_configuration(self, frequency, power, bandwidth):
		self.settings = (frequency, power, bandwidth)

	def recv(self, timeout=None):
		try:
			data = self.rx_queue.get(timeout=.01)
		except Queue.Empty:
			self.testbed.clock += timeout
			raise RadioTimeout
		else:
			return RadioPacket(data)

class MockSandboxedPlayer(object):
	def __init__(self, rx, tx, i):
		self.rx = rx
		self.tx = tx
		self.i = i

class MockSandboxedTransceiver(object):
	def __init__(self, cls, role):
		self.cls = cls
		self.role = role

	def init(self, i, update_interval):
		self.ins = self.cls(i, self.role, update_interval)

	def start(self, client):
		self.ins._start(client)

	def join(self):
		self.ins._join()

class MockSandbox(object):
	def __init__(self, rxcls, txcls):
		self.player = MockSandboxedPlayer(
				MockSandboxedTransceiver(rxcls, 'rx'),
				MockSandboxedTransceiver(txcls, 'tx'), 0)

	def get_players(self):
		return [self.player]

class TestGame(unittest.TestCase):

	PACKET_LIMIT = 50
	TIME_LIMIT = 50
	PAYLOAD_LIMIT = 200*10

	def setUp(self):
		self.testbed = MockTestbed()

	def _run_game(self, rxcls, txcls, packet_limit=PACKET_LIMIT, payload_limit=PAYLOAD_LIMIT,
			time_limit=TIME_LIMIT):

		sandbox = MockSandbox(rxcls, txcls)
		game = Game(self.testbed, sandbox,
				packet_limit=packet_limit,
				time_limit=time_limit,
				payload_limit=payload_limit)
		ctl = GameController()
		return ctl.run(game)[0]

	def test_timeout(self):

		class Receiver(Transceiver):
			pass

		class Transmitter(Transceiver):
			pass

		result = self._run_game(Receiver, Transmitter)
		self.assertEqual(result.received_packets, 0)

	def test_one_packet(self):

		class Receiver(Transceiver):
			def start(self):
				self.set_configuration(2.4e9, 0, 100e3)

		class Transmitter(Transceiver):
			def start(self):
				self.set_configuration(2.4e9, 0, 100e3)
				self.send()

		result = self._run_game(Receiver, Transmitter)
		self.assertEqual(result.received_packets, 1)
		self.assertEqual(result.payload_bytes, self.testbed.get_packet_size())

	def test_one_packet_reverse(self):

		class Receiver(Transceiver):
			def start(self):
				self.send()

		result = self._run_game(Receiver, Transceiver)
		self.assertEqual(result.received_packets, 1)
		self.assertEqual(result.payload_bytes, 0)

	def test_one_packet_miss(self):

		class Receiver(Transceiver):
			def start(self):
				self.set_configuration(2.4e9, 0, 100e3)

		class Transmitter(Transceiver):
			def start(self):
				self.set_configuration(2.5e9, 0, 100e3)
				self.send()

		result = self._run_game(Receiver, Transmitter)
		self.assertEqual(result.received_packets, 0)

	def test_all_packets(self):

		class Receiver(Transceiver):
			def start(self):
				self.set_configuration(2.4e9, 0, 100e3)

		class Transmitter(Transceiver):
			def start(self):
				self.set_configuration(2.4e9, 0, 100e3)

				while True:
					self.send()

		result = self._run_game(Receiver, Transmitter, payload_limit=None, time_limit=None)
		self.assertGreaterEqual(result.received_packets, self.PACKET_LIMIT)

	def test_all_payload(self):

		class Transmitter(Transceiver):
			def start(self):
				while True:
					self.send()

		result = self._run_game(Transceiver, Transmitter, packet_limit=None, time_limit=None)
		self.assertGreaterEqual(result.payload_bytes, self.PAYLOAD_LIMIT)

	def test_recv_packet(self):

		cnt = [0]

		class Receiver(Transceiver):
			def start(self):
				self.set_configuration(2.4e9, 0, 100e3)

			def recv(self, packet):
				cnt[0] += 1

		class Transmitter(Transceiver):
			def start(self):
				self.set_configuration(2.4e9, 0, 100e3)
				self.send()

		result = self._run_game(Receiver, Transmitter)
		self.assertEqual(cnt[0], 1)

	def test_recv_packet_data(self):

		cnt = [0]
		foo = "foo"

		class Receiver(Transceiver):
			def start(self):
				self.set_configuration(2.4e9, 0, 100e3)

			def recv(self, packet):
				cnt[0] = packet

		class Transmitter(Transceiver):
			def start(self):
				self.set_configuration(2.4e9, 0, 100e3)
				self.send(foo)

		result = self._run_game(Receiver, Transmitter)
		self.assertEqual(cnt[0].data, foo)
		self.assertEqual(result.payload_bytes, self.testbed.get_packet_size() - len(foo))

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

	def test_too_long_packet_data(self):

		foo = "x" * (self.testbed.get_packet_size() + 1)

		class Transmitter(Transceiver):
			def start(self):
				self.send(foo)


		log_exc_off()
		result = self._run_game(Transceiver, Transmitter)
		log_exc_on()
		self.assertTrue(result.crashed)

	def test_status(self):

		cnt = [0]

		class Receiver(Transceiver):
			def status_update(self, status):
				cnt[0] += 1

		result = self._run_game(Receiver, Transceiver)
		self.assertGreater(cnt[0], 1)
		#self.assertEqual(cnt[0], self.TIME_LIMIT)

	def test_get_packet_size(self):

		cnt = [0]

		class Receiver(Transceiver):
			def start(self):
				cnt[0] = self.get_packet_size()

		result = self._run_game(Receiver, Transceiver)
		self.assertEqual(cnt[0], self.testbed.get_packet_size())

	def test_error_recv(self):

		class Receiver(Transceiver):
			def recv(self, packet):
				raise Exception

		class Transmitter(Transceiver):
			def start(self):
				while True:
					self.send()

		log_exc_off()
		result = self._run_game(Receiver, Transmitter)
		log_exc_on()
		self.assertEqual(result.crashed, True)

	def test_error_start(self):

		class Receiver(Transceiver):
			def start(self):
				raise Exception

		log_exc_off()
		result = self._run_game(Receiver, Transceiver)
		log_exc_on()
		self.assertEqual(result.crashed, True)

	def test_error_status_update(self):

		class Receiver(Transceiver):
			def status_update(self, status):
				raise Exception

		log_exc_off()
		result = self._run_game(Receiver, Transceiver)
		log_exc_on()
		self.assertEqual(result.crashed, True)

	def test_recv_in_start(self):

		cnt = [0, 0, 0]

		class Receiver(Transceiver):
			def start(self):
				for data in self.recv_loop(timeout=2.):
					cnt[1] += 1

			def recv(self, packet):
				cnt[0] += 1

		class Transmitter(Transceiver):
			def start(self):
				while True:
					cnt[2] += 1
					self.send()

		result = self._run_game(Receiver, Transmitter, payload_limit=None)

		self.assertEqual(result.crashed, False)
		self.assertGreaterEqual(cnt[0], self.PACKET_LIMIT)
		self.assertGreaterEqual(cnt[1], self.PACKET_LIMIT)
		self.assertGreaterEqual(cnt[2], self.PACKET_LIMIT)

	def test_status_update(self):

		sl = []

		class Receiver(Transceiver):
			def status_update(self, status):
				sl.append(status)

		self._run_game(Receiver, Transceiver)

		for s in sl:
			self.assertTrue(s.spectrum)

if __name__ == '__main__':
	unittest.main()
