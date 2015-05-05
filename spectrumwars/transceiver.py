from spectrumwars.game import StopGame, RadioTimeout

class Transceiver(object):

	def __init__(self, game, i, role, radio):
		self._game = game
		self._player = game.players[i]
		self._i = i
		self._role = role
		self._radio = radio

		self._settings = None

	def start(self):
		pass

	def status_update(self, status):
		pass

	def set_configuration(self, frequency, power, bandwidth):
		self._radio.set_configuration(frequency, power, bandwidth)

	def send(self, data=None):
		self._radio.send(data)

		if self._game.state != 'running':
			raise StopGame

	def _recv(self):
		while True:
			try:
				data = self._radio.recv()
			except RadioTimeout:
				break

			self._player.result.packets += 1

			if self._player.result.packets >= self._game.packet_limit:
				raise StopGame

			self.recv(data)

	def recv(self, data):
		pass
