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

	def reconfigure(self, frequency, power, bandwidth):
		self._settings = (frequency, power, bandwidth)

	def send(self):
		self._player.rx._recv(self._settings)

	def _recv(self, settings):
		if self._settings == settings:
			self._player.result.packets += 1

			if self._player.result.packets >= self._game.packet_num:
				raise StopGame

			self.recv()

	def recv(self):
		pass
