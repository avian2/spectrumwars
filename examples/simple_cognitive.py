from spectrumwars import Transceiver
import time
import numpy as np

class Source(Transceiver):
	def start(self):
		time.sleep(.2)
		spectrum = np.array( self.get_status().spectrum )
		ch = np.argmin(spectrum)

		self.set_configuration(ch, 0, 0)

		while True:
			self.send()

class Destination(Transceiver):
	def start(self):
		while True:
			time.sleep(.3)
			spectrum = np.array( self.get_status().spectrum )

			chl = np.argsort(spectrum)[::-1]
			for ch in chl[:10]:
				self.set_configuration(ch, 0, 0)

				for packet in self.recv_loop(timeout=.2):
					pass
