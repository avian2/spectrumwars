from spectrumwars import Transceiver
import random
import time
import numpy as np

class Source(Transceiver):
	def start(self):
		while True:
			spectrum = np.array( self.get_status().spectrum )

			chl = np.argsort(spectrum)

			ch = chl[random.randint(0, 20)]

			self.send(chr(ch))
			self.set_configuration(ch, 0, 0)
			for n in xrange(9):
				self.send()

class Destination(Transceiver):
	def start(self):
		time.sleep(.2)
		while True:
			time.sleep(.1)
			spectrum = np.array( self.get_status().spectrum )

			chl = np.argsort(spectrum)[::-1]
			for ch in chl[:5]:
				self.set_configuration(ch, 0, 0)

				found = False
				for packet in self.recv_loop(timeout=.2):
					found = True

					if packet.data:
						ch = ord(packet.data[0])
						self.set_configuration(ch, 0, 0)

				if found:
					break
