from spectrumwars import Transceiver

class Receiver(Transceiver):
	def recv(self, data):
		assert data == 'foo'

class Transmitter(Transceiver):
	def start(self):
		while True:
			self.send("foo")
