import threading

class StopGame(Exception): pass

class Testbed(object):
	def get_radio_pair(self):
		pass

class Radio(object):
	def __init__(self, neighbor):
		pass

	def send(self):
		pass

	def set_configuration(self):
		pass

	def recv(self, timeout=2.):
		pass

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

	def __init__(self, players, packet_limit=100, time_limit=100):
		self.players = players
		self.packet_limit = packet_limit
		self.time_limit = time_limit

	def instantiate(self):
		for i, player in enumerate(self.players):
			player.instantiate(self, i)

class GameStatus(object):
	pass

class GameController(object):
	def __init__(self):
		pass

	def run(self, game):

		game.instantiate()

		workers = []

		for player in game.players:
			for transceiver in player.rx, player.tx:
				worker = threading.Thread(target=self.worker, args=(game, transceiver))
				worker.start()

				workers.append(worker)

		for worker in workers:
			worker.join()

		return [ player.result for player in game.players ]

	def worker(self, game, transceiver):

		try:
			transceiver.start()

			for i in xrange(game.time_limit):
				status = GameStatus()
				transceiver.status_update(status)

		except StopGame:
			pass
