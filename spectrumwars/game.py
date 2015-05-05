import logging
import threading
import time

log = logging.getLogger(__name__)

class StopGame(Exception): pass

class Player(object):
	def __init__(self, rxcls, txcls):
		self.rxcls = rxcls
		self.txcls = txcls

	def instantiate(self, game, i):
		rxradio, txradio = game.testbed.get_radio_pair()

		self.rx = self.rxcls(game, i, 'rx', rxradio)
		self.tx = self.txcls(game, i, 'tx', txradio)

		self.result = PlayerResult()

class PlayerResult(object):
	def __init__(self, packets=0):
		self.packets = packets

class Game(object):

	def __init__(self, testbed, players, packet_limit=100, time_limit=100):
		self.testbed = testbed
		self.players = players
		self.packet_limit = packet_limit
		self.time_limit = time_limit

		self.state = 'new'

	def instantiate(self):
		for i, player in enumerate(self.players):
			player.instantiate(self, i)

class GameStatus(object):
	pass

class GameController(object):
	def __init__(self):
		pass

	def run(self, game):

		log.debug("Instantiating player classes")
		game.instantiate()

		transceivers = []
		workers = []

		game.state = 'running'

		for player in game.players:
			for transceiver in player.rx, player.tx:
				transceivers.append(transceiver)

				worker = threading.Thread(target=self.worker, args=(game, transceiver))
				worker.start()

				workers.append(worker)

		for worker in workers:
			worker.join()

		log.debug("Cleaning up transceivers")

		# clean up any remaining packets in queues
		for transceiver in transceivers:
			try:
				transceiver._recv()
			except StopGame:
				pass

			transceiver._stop()

		game.state = 'finished'

		log.debug("Game concluded")

		return [ player.result for player in game.players ]

	def worker(self, game, transceiver):

		name = "(%d %s)" % (transceiver._i, transceiver._role)

		log.debug("%s worker started" % name)

		try:
			transceiver.start()

			for i in xrange(game.time_limit):
				transceiver._recv()

				log.debug("%s status update (%d/%d)" % (name, i, game.time_limit))

				status = GameStatus()
				transceiver.status_update(status)

				if game.state != 'running':
					log.debug("%s stopping game" % name)
					break

			log.debug("%s reached time limit" % name)

		except StopGame:
			log.debug("%s wants to stop game" % name)

		game.state = 'stopping'
