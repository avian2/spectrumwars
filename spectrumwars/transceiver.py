from spectrumwars.game import StopGame

class Transceiver(object):

	def __init__(self, game, i, role):
		self._game = game
		self._player = game.players[i]
		self._i = i
		self._role = role

		self._settings = None

	def start(self):
		pass

	def status_update(self, status):
		pass

	def set_configuration(self, frequency, power, bandwidth):
		self._settings = (frequency, power, bandwidth)

	def send(self, data=None):
		self._player.rx._recv(self._settings, data)

	def _recv(self, settings, data):
		if self._settings == settings:
			self._player.result.packets += 1

			if self._player.result.packets >= self._game.packet_limit:
				raise StopGame

			self.recv(data)

	def recv(self, data):
		pass
