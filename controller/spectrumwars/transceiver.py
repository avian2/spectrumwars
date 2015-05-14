import logging

from spectrumwars.game import StopGame
from spectrumwars.testbed import RadioTimeout

log = logging.getLogger(__name__)

class Transceiver(object):

	def __init__(self, game, i, role, radio):
		self._game = game
		self._player = game.players[i]
		self._radio = radio

		self._i = i
		self._role = role
		self._name = "(%d %s)" % (self._i, self._role)

		self._settings = None

	def _safe_call(self, f, *args, **kwargs):
		try:
			f(*args, **kwargs)
		except StopGame:
			raise
		except:
			self._player.result.crashed = True
			log.warning("%s crashed" % (self._name,), exc_info=True)
			raise StopGame

	def _start(self):
		self._safe_call(self.start)

	def start(self):
		pass

	def _status_update(self, status):
		self._safe_call(self.status_update, status)

	def status_update(self, status):
		pass

	def get_status(self):
		return self._game.get_status(self._i, self._role)

	def set_configuration(self, frequency, bandwidth, power):
		self._game.log_event("config", i=self._i, role=self._role,
				frequency=frequency, bandwidth=bandwidth, power=power)

		self._radio.set_configuration(frequency, bandwidth, power)

	def send(self, data=None):
		self._game.log_event("send", i=self._i, role=self._role)
		self._radio.send(data)

		self._player.result.transmit_packets += 1

		if self._game.should_finish():
			raise StopGame

	def _recv(self, timeout):
		for data in self.recv_loop(timeout):
			pass

	def recv_loop(self, timeout=1.):
		while True:
			try:
				data = self._radio.recv(timeout=timeout)
			except RadioTimeout:
				break

			self._player.result.received_packets += 1

			if self._role == 'rx':
				payload_bytes = self.get_packet_size()
				if data:
					payload_bytes -= len(data)
				self._player.result.payload_bytes += payload_bytes

			self._game.log_event("recv",  i=self._i, role=self._role)

			self._safe_call(self.recv, data)

			yield data

		if self._game.should_finish():
			raise StopGame

	def recv(self, data):
		pass

	def _stop(self):
		self._radio.stop()

	def get_packet_size(self):
		return self._game.testbed.get_packet_size()
