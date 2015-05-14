class TestbedError(Exception): pass
class RadioError(Exception): pass
class RadioTimeout(Exception): pass

class TestbedBase(object):
	def get_radio_pair(self):
		raise NotImplementedError

	def time(self):
		raise NotImplementedError

	def start(self):
		pass

	def stop(self):
		pass

	def get_spectrum(self):
		raise NotImplementedError

	def get_packet_size(self):
		raise NotImplementedError

class RadioBase(object):
	def send(self, data):
		pass

	def set_configuration(self, frequency, power, bandwidth):
		pass

	def recv(self, timeout=None):
		raise NotImplementedError

	def start(self):
		pass

	def stop(self):
		pass
