from spectrumwars import Transceiver

class Destination(Transceiver):
	def start(self):
		self.set_configuration(0, 0, 0)

class Source(Transceiver):
	def start(self):
		self.set_configuration(0, 0, 0)
		while True:
			self.send()
