from spectrumwars import Transceiver
import random

class Transmitter(Transceiver):
	def start(self):
		ch = random.randint(0, 40)
		self.set_configuration(ch, 3, 0)

		while True:
			self.send()

class Receiver(Transceiver):
	def start(self):
		ch = 0

		while True:
			self.set_configuration(ch, 3, 0)

			for packet in self.recv_loop(timeout=.5):
				pass

			ch = (ch + 1) % 40
