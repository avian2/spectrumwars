from spectrumwars import Transceiver

class Receiver(Transceiver):
	def start(self):
		self.set_configuration(0, 0, 0)

	def recv(self, data):
		assert data == 'foo'

class Transmitter(Transceiver):
	def start(self):
		self.set_configuration(0, 1, 0)
		while True:
			self.send("foo")
