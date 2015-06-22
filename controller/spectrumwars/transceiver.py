import logging
import threading
import traceback

from spectrumwars.testbed import RadioTimeout, RadioError, RadioPacket, GameStatus

log = logging.getLogger(__name__)

class TransceiverError(Exception):
	def __init__(self, desc):
		self.desc = desc

class StopGame(Exception): pass

class Transceiver(object):

	def __init__(self, i, role, update_interval):
		self._update_interval = update_interval

		self._i = i
		self._role = role
		self._name = "(%d %s)" % (self._i, self._role)

		self._packet_size = None

	def _safe_call(self, f, *args, **kwargs):
		try:
			f(*args, **kwargs)
		except StopGame:
			raise
		except:
			log.warning("%s crashed" % (self._name,), exc_info=True)
			raise TransceiverError(traceback.format_exc())

	def _start(self, client):
		self._client = client

		self._frequency_range, \
				self._bandwidth_range, \
				self._power_range = self._client.get_ranges()

		self._event_loop()

	def start(self):
		pass

	def status_update(self, status):
		pass

	def get_status(self):
		status_json = self._client.get_status()
		status = GameStatus.from_json(status_json)

		self._safe_call(self.status_update, status)
		return status

	def set_configuration(self, frequency, bandwidth, power):
		if frequency < 0 or frequency >= self._frequency_range:
			raise RadioError("invalid frequency (%d not in range 0-%d)" % (
				frequency, self._frequency_range))
		if bandwidth < 0 or bandwidth >= self._bandwidth_range:
			raise RadioError("invalid bandwidth (%d not in range 0-%d)" % (
				bandwidth, self._bandwidth_range))
		if power < 0 or power >= self._power_range:
			raise RadioError("invalid power (%d not in range 0-%d)" % (
				power, self._power_range))

		self._client.set_configuration(frequency, bandwidth, power)

	def get_configuration(self):
		return self._client.get_configuration()

	def get_frequency_range(self):
		return self._frequency_range

	def get_bandwidth_range(self):
		return self._bandwidth_range

	def get_power_range(self):
		return self._power_range

	def send(self, data=None):
		if data and len(data) > self.get_packet_size():
			raise RadioError("packet too long")

		self._client.send(data)

		if self._client.should_finish():
			raise StopGame

	def _recv(self, timeout):
		for packet in self.recv_loop(timeout):
			pass

	def recv_loop(self, timeout=1.):
		while True:
			packet_json = self._client.recv(timeout=timeout)
			if packet_json is None:
				break

			packet = RadioPacket.from_json(packet_json)

			self._safe_call(self.recv, packet)

			yield packet

		if self._client.should_finish():
			raise StopGame

	def recv(self, packet):
		pass

	def get_packet_size(self):
		if self._packet_size is None:
			self._packet_size = self._client.get_packet_size()

		return self._packet_size

	def _event_loop(self):

		log.debug("%s worker started" % (self._name,))

		crashed = False
		desc = None

		try:
			self._safe_call(self.start)

			i = 0
			while not self._client.should_finish():

				self._recv(timeout=self._update_interval)

				log.debug("%s status update (%d)" % (self._name, i))

				self.get_status()

				i += 1

		except StopGame:
			pass
		except TransceiverError, e:
			crashed = True
			desc = e.desc

		log.debug("%s worker stopped" % self._name)

		self._client.report_stop(crashed, desc)
