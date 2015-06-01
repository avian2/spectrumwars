import logging
import threading

from spectrumwars.game import StopGame
from spectrumwars.testbed import RadioTimeout, RadioError

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
		self._packet_size = None

	def _safe_call(self, f, *args, **kwargs):
		try:
			f(*args, **kwargs)
		except StopGame:
			raise
		except:
			self._player.result.crashed = True
			log.warning("%s crashed" % (self._name,), exc_info=True)
			raise StopGame

	def _start(self, client):
		self._client = client

		self._thread = threading.Thread(target=self._event_loop)
		self._thread.start()

	def _join(self):
		self._thread.join()

	def start(self):
		pass

	def status_update(self, status):
		pass

	def get_status(self):
		status = self._client.get_status(self._i, self._role)
		self._safe_call(self.status_update, status)
		return status

	def set_configuration(self, frequency, bandwidth, power):
		self._client.set_configuration(frequency, bandwidth, power)

	def send(self, data=None):
		if data and len(data) > self.get_packet_size():
			raise RadioError("packet too long")

		self._client.send(data)

		if self._game.should_finish():
			raise StopGame

	def _recv(self, timeout):
		for packet in self.recv_loop(timeout):
			pass

	def recv_loop(self, timeout=1.):
		while True:
			packet = self._client.recv(timeout=timeout)
			if packet is None:
				break

			self._safe_call(self.recv, packet)

			yield packet

		if self._game.should_finish():
			raise StopGame

	def recv(self, packet):
		pass

	def get_packet_size(self):
		if self._packet_size is None:
			self._packet_size = self._client.get_packet_size()

		return self._packet_size

	def _event_loop(self):

		log.debug("%s worker started" % (self._name,))

		try:
			self._safe_call(self.start)

			i = 0
			while not self._game.should_finish():

				self._recv(timeout=self._game.update_interval)

				log.debug("%s status update (%d)" % (self._name, i))

				self.get_status()

				i += 1

		except StopGame:
			pass

		log.debug("%s worker stopped" % self._name)
		self._game.state = 'stopping'
