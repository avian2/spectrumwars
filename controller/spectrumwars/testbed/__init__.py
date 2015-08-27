import time

class TestbedError(Exception): pass
class RadioError(Exception): pass
class RadioTimeout(Exception): pass

class TestbedBase(object):
	def get_radio_pair(self):
		raise NotImplementedError

	def time(self):
		return time.time()

	def start(self):
		pass

	def stop(self):
		pass

	def get_spectrum(self):
		raise NotImplementedError

	def get_packet_size(self):
		return self.RADIO_CLASS.PACKET_SIZE - 1

	def get_frequency_range(self):
		raise NotImplementedError

	def get_bandwidth_range(self):
		raise NotImplementedError

	def get_power_range(self):
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

class RadioPacket(object):
	def __init__(self, data):
		self.data = data

	def to_json(self):
		return (self.data,)

	@classmethod
	def from_json(cls, json):
		return cls(*json)

class GameStatus(object):
	def __init__(self, spectrum):
		self.spectrum = spectrum

	def to_json(self):
		return (self.spectrum,)

	@classmethod
	def from_json(cls, json):
		return cls(*json)
