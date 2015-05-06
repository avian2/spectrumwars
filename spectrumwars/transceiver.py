import logging

from spectrumwars.game import StopGame
from spectrumwars.testbed import RadioTimeout

log = logging.getLogger(__name__)

class Transceiver(object):

	def __init__(self, game, i, role, radio):
		self._game = game
		self._player = game.players[i]
		self._i = i
		self._role = role
		self._radio = radio

		self._settings = None

	def _safe_call(self, f, *args, **kwargs):
		try:
			f(*args, **kwargs)
		except StopGame:
			raise
		except:
			self._player.result.crashed = True
			log.warning("(%d %s) crashed" % (self._i, self._role), exc_info=True)
			raise StopGame

	def _start(self):
		self._safe_call(self.start)

	def start(self):
		pass

	def _status_update(self, status):
		self._safe_call(self.status_update, status)

	def status_update(self, status):
		pass

	def set_configuration(self, frequency, bandwidth, power):
		self._radio.set_configuration(frequency, bandwidth, power)

	def send(self, data=None):
		self._radio.send(data)

		self._player.result.transmit_packets += 1

		if self._game.state != 'running':
			raise StopGame

	def _recv(self):
		for data in self.recv_loop():
			pass

	def recv_loop(self, timeout=1.):
		while True:
			try:
				data = self._radio.recv()
			except RadioTimeout:
				break

			self._player.result.received_packets += 1

			self._safe_call(self.recv, data)

			yield data

			if self._player.result.received_packets >= self._game.packet_limit:
				raise StopGame

	def recv(self, data):
		pass

	def _stop(self):
		self._radio.stop()
