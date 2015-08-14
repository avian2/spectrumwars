import logging
import Queue
import random
import time

from spectrumwars.testbed import TestbedBase, RadioBase, RadioTimeout, RadioError, TestbedError, RadioPacket

log = logging.getLogger(__name__)

class Radio(RadioBase):
	RECEIVE_TIMEOUT = 2.

	def __init__(self, addr, dispatcher):
		self.addr = addr
		self.neighbor = None
		self.dispatcher = dispatcher
		self.q = Queue.Queue()
		self.settings = (0, 0, 0)

	def _recv(self, addr, data, settings):
		if self.settings == settings and self.addr == addr:
			self.q.put(data)

	def set_configuration(self, frequency, power, bandwidth):
		self.settings = (frequency, power, bandwidth)

	def send(self, data):
		self.dispatcher(self.neighbor, data, self.settings)
		time.sleep(.1)

	def recv(self, timeout=None):
		if timeout is None:
			timeout = self.RECEIVE_TIMEOUT

		try:
			data = self.q.get(True, timeout)
		except Queue.Empty:
			raise RadioTimeout
		else:
			return RadioPacket(data)

class Testbed(TestbedBase):

	def __init__(self):
		self.radios = []
		self.channels = [0] * self.get_frequency_range()
		self.i = 0

	def _get_radio(self):
		r = Radio(self.i, self._dispatcher)
		self.radios.append(r)

		self.i += 1

		return r

	def _dispatcher(self, addr, data, settings):
		self.channels[settings[0]] = self.time()

		for radio in self.radios:
			radio._recv(addr, data, settings)

	def get_radio_pair(self):
		rx = self._get_radio()
		tx = self._get_radio()

		rx.neighbor = tx.addr
		tx.neighbor = rx.addr

		return rx, tx

	def get_spectrum(self):

		spectrum = []
		now = self.time()

		for time in self.channels:
			if now - time < .5:
				p = random.randint(-40, -20)
			else:
				p = random.randint(-90, -80)

			spectrum.append(p)

		return tuple(spectrum)

	def get_frequency_range(self):
		return 64

	def get_bandwidth_range(self):
		return 10

	def get_power_range(self):
		return 10

	def get_packet_size(self):
		return 1024
