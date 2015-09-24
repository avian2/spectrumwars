from spectrumwars import Transceiver
import random
import time
import numpy as np

class Source(Transceiver):
	def start(self):
		while True:
			time.sleep(.2)
			spectrum = np.array( self.get_status().spectrum )

			chl = np.argsort(spectrum)

			ch = chl[random.randint(0, 20)]

			self.set_configuration(ch, 0, 0)
			for n in xrange(20):
				self.send()
				time.sleep(.05)

class Destination(Transceiver):
	def start(self):
		time.sleep(.2)
		while True:
			time.sleep(.1)
			spectrum = np.array( self.get_status().spectrum )

			chl = np.argsort(spectrum)[::-1]
			for ch in chl[:5]:
				self.set_configuration(ch, 0, 0)

				for packet in self.recv_loop(timeout=.2):
					pass
