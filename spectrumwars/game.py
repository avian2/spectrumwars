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
	def __init__(self):
		self.received_packets = 0
		self.transmit_packets = 0
		self.crashed = False

class Game(object):

	def __init__(self, testbed, players, packet_limit=100, time_limit=100):
		self.testbed = testbed
		self.players = players
		self.packet_limit = packet_limit
		self.time_limit = time_limit

		self.update_interval = 1
		self.start_time = None
		self.end_time = None

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

		game.start_time = game.testbed.time()

		for player in game.players:
			for transceiver in player.rx, player.tx:
				transceivers.append(transceiver)

				worker = threading.Thread(target=self.worker, args=(game, transceiver))
				worker.start()

				workers.append(worker)

		for worker in workers:
			worker.join()

		self.end_time = game.testbed.time()

		log.debug("Cleaning up transceivers")

		# clean up any remaining packets in queues
		for transceiver in transceivers:
			try:
				transceiver._recv(timeout=0.1)
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
			transceiver._start()

			i = 0
			while game.testbed.time() - game.start_time < game.time_limit:

				transceiver._recv(timeout=game.update_interval)

				log.debug("%s status update (%d)" % (name, i))

				status = GameStatus()
				transceiver._status_update(status)

				if game.state != 'running':
					log.debug("%s stopping game" % name)
					break
			else:
				log.debug("%s reached time limit" % name)

		except StopGame:
			log.debug("%s wants to stop game" % name)

		game.state = 'stopping'
