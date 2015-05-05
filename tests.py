import unittest

import Queue
from spectrumwars import Transceiver, Player, Game, GameController, RadioTimeout

class MockTestbed(object):
	def get_radio_pair(self):

		rxradio = MockRadio()
		txradio = MockRadio()

		rxradio.neighbor = txradio
		txradio.neighbor = rxradio

		return rxradio, txradio

class MockRadio(object):
	def __init__(self):
		self.neighbor = None

		self.settings = None
		self.rx_queue = Queue.Queue()

	def send(self, data):
		if self.settings == self.neighbor.settings:
			self.neighbor.rx_queue.put(data)

	def set_configuration(self, frequency, power, bandwidth):
		self.settings = (frequency, power, bandwidth)

	def recv(self, timeout=1.):
		try:
			data = self.rx_queue.get(block=False)
		except Queue.Empty:
			raise RadioTimeout
		else:
			return data

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
		self.assertEqual(result.packets, 0)

	def test_one_packet(self):

		class Receiver(Transceiver):
			def start(self):
				self.set_configuration(2.4e9, 0, 100e3)

		class Transmitter(Transceiver):
			def start(self):
				self.set_configuration(2.4e9, 0, 100e3)
				self.send()

		result = self._run_game(Receiver, Transmitter)
		self.assertEqual(result.packets, 1)

	def test_one_packet_miss(self):

		class Receiver(Transceiver):
			def start(self):
				self.set_configuration(2.4e9, 0, 100e3)

		class Transmitter(Transceiver):
			def start(self):
				self.set_configuration(2.5e9, 0, 100e3)
				self.send()

		result = self._run_game(Receiver, Transmitter)
		self.assertEqual(result.packets, 0)

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
		self.assertGreater(result.packets, 0)
		#self.assertEqual(result.packets, self.PACKET_LIMIT)

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

if __name__ == '__main__':
	unittest.main()
