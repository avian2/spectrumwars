import unittest

from spectrumwars import Transceiver, Player, Game, GameController

class TestGame(unittest.TestCase):

	PACKET_LIMIT = 50
	TIME_LIMIT = 50

	def _run_game(self, rxcls, txcls):
		player = Player(rxcls, txcls)
		game = Game([player], packet_limit=self.PACKET_LIMIT, time_limit=self.TIME_LIMIT)
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
		self.assertEqual(result.packets, self.PACKET_LIMIT)

	def test_recv_packet(self):

		cnt = [0]

		class Receiver(Transceiver):
			def start(self):
				self.set_configuration(2.4e9, 0, 100e3)

			def recv(self):
				cnt[0] += 1

		class Transmitter(Transceiver):
			def start(self):
				self.set_configuration(2.4e9, 0, 100e3)
				self.send()

		result = self._run_game(Receiver, Transmitter)
		self.assertEqual(cnt[0], 1)

	def test_status(self):

		cnt = [0]

		class Receiver(Transceiver):
			def status_update(self, status):
				cnt[0] += 1

		result = self._run_game(Receiver, Transceiver)
		self.assertEqual(cnt[0], self.TIME_LIMIT)

if __name__ == '__main__':
	unittest.main()
