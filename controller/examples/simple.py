from spectrumwars import Transceiver

class Receiver(Transceiver):
	def start(self):
		self.set_configuration(0, 0, 0)

class Transmitter(Transceiver):
	def start(self):
		self.set_configuration(0, 0, 0)
		while True:
			self.send()
