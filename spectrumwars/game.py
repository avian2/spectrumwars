class StopGame(Exception): pass

class Player(object):
	def __init__(self, rxcls, txcls):
		self.rxcls = rxcls
		self.txcls = txcls

	def instantiate(self, game, i):
		self.rx = self.rxcls(game, i, 'rx')
		self.tx = self.txcls(game, i, 'tx')

		self.result = PlayerResult()

class PlayerResult(object):
	def __init__(self, packets=0):
		self.packets = packets

class Game(object):
	packet_num = 100

	def __init__(self, players):
		self.players = players

	def instantiate(self):
		for i, player in enumerate(self.players):
			player.instantiate(self, i)

class GameController(object):
	def __init__(self):
		pass

	def run(self, game):

		game.instantiate()

		try:
			for player in game.players:
				player.rx.start()
				player.tx.start()
		except StopGame:
			pass

		return [ player.result for player in game.players ]
