import Queue

class RadioTimeout(Exception): pass

class Testbed(object):
	def get_radio_pair(self):

		rxradio = MockRadio()
		txradio = MockRadio()

		rxradio.neighbor = txradio
		txradio.neighbor = rxradio

		return rxradio, txradio

class MockRadio(object):
	def __init__(self):
		self.neighbor = None

		self.settings = None
		self.rx_queue = Queue.Queue()

	def send(self, data):
		if self.settings == self.neighbor.settings:
			self.neighbor.rx_queue.put(data)

	def set_configuration(self, frequency, power, bandwidth):
		self.settings = (frequency, power, bandwidth)

	def recv(self, timeout=1.):
		try:
			data = self.rx_queue.get(block=False)
		except Queue.Empty:
			raise RadioTimeout
		else:
			return data
