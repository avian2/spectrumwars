import logging
import unittest

import Queue
from spectrumwars import Transceiver, Player, Game, GameController, RadioTimeout

level = logging.INFO
logging.basicConfig(level=level)

def log_exc_off():
	logging.getLogger().setLevel(logging.ERROR)

def log_exc_on():
	logging.getLogger().setLevel(level)


class MockTestbed(object):
	def get_radio_pair(self):

		rxradio = MockRadio(self)
		txradio = MockRadio(self)

		rxradio.neighbor = txradio
		txradio.neighbor = rxradio

		self.clock = 0.

		return rxradio, txradio

	def time(self):
		return self.clock

	def start(self):
		pass

	def stop(self):
		pass

	def get_spectrum(self):
		return True

class MockRadio(object):
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
			return data

	def stop(self):
		pass

class TestGame(unittest.TestCase):

	PACKET_LIMIT = 50
	TIME_LIMIT = 50

	def _run_game(self, rxcls, txcls):
		testbed = MockTestbed()
		player = Player(rxcls, txcls)
		game = Game(testbed, [player], packet_limit=self.PACKET_LIMIT, time_limit=self.TIME_LIMIT)
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

		result = self._run_game(Receiver, Transmitter)
		self.assertGreater(result.received_packets, 0)
		#self.assertEqual(result.received_packets, self.PACKET_LIMIT)

	def test_recv_packet(self):

		cnt = [0]

		class Receiver(Transceiver):
			def start(self):
				self.set_configuration(2.4e9, 0, 100e3)

			def recv(self, data):
				cnt[0] += 1

		class Transmitter(Transceiver):
			def start(self):
				self.set_configuration(2.4e9, 0, 100e3)
				self.send()

		result = self._run_game(Receiver, Transmitter)
		self.assertEqual(cnt[0], 1)

	def test_recv_packet_data(self):

		cnt = [0]

		class Receiver(Transceiver):
			def start(self):
				self.set_configuration(2.4e9, 0, 100e3)

			def recv(self, data):
				cnt[0] = data

		class Transmitter(Transceiver):
			def start(self):
				self.set_configuration(2.4e9, 0, 100e3)
				self.send("foo")

		result = self._run_game(Receiver, Transmitter)
		self.assertEqual(cnt[0], "foo")

	def test_status(self):

		cnt = [0]

		class Receiver(Transceiver):
			def status_update(self, status):
				cnt[0] += 1

		result = self._run_game(Receiver, Transceiver)
		self.assertGreater(cnt[0], 1)
		#self.assertEqual(cnt[0], self.TIME_LIMIT)

	def test_error_recv(self):

		class Receiver(Transceiver):
			def recv(self, data):
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

				print "exit"

			def recv(self, data):
				cnt[0] += 1

		class Transmitter(Transceiver):
			def start(self):
				while True:
					self.send()
					cnt[2] += 1

		result = self._run_game(Receiver, Transmitter)

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
