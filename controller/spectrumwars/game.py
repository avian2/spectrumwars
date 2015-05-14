import logging
import threading
import time
from spectrumwars.testbed import TestbedError

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
		# number of received packets in both directions
		self.received_packets = 0
		# number of transmitted packets in both directions
		self.transmit_packets = 0
		# whether the player's code raised an unhandled exception
		self.crashed = False
		# number of bytes transferred from transmitter to receiver
		self.payload_bytes = 0

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

		self.log = []

	def should_finish(self):

		if self.testbed.time() - self.start_time > self.time_limit:
			log.debug("game time limit reached!")
			return True

		for player in self.players:
			if player.result.received_packets >= self.packet_limit:
				log.debug("game packet limit reached by player %d!" %
						player.rx._i)
				return True

		if self.state != 'running':
			return True

		return False

	def instantiate(self):
		for i, player in enumerate(self.players):
			player.instantiate(self, i)

	def log_event(self, type, **kwargs):
		event = GameEvent(type, **kwargs)
		event.timestamp = self.testbed.time()
		self.log.append(event)

	def get_status(self, i, role):
		status = GameStatus(self.testbed.get_spectrum())
		self.log_event("status", i=i, role=role, status=status)

		return status

class GameEvent(object):
	def __init__(self, type, **kwargs):
		self.type = type
		self.timestamp = None
		self.data = kwargs

class GameStatus(object):
	def __init__(self, spectrum):
		self.spectrum = spectrum

class GameController(object):
	def __init__(self):
		pass

	def run(self, game):

		log.debug("Instantiating player classes")
		game.instantiate()
		game.testbed.start()

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

		game.end_time = game.testbed.time()

		log.debug("Cleaning up transceivers")

		# clean up any remaining packets in queues
		for transceiver in transceivers:
			try:
				transceiver._recv(timeout=0.1)
			except StopGame:
				pass

		game.testbed.stop()
		game.state = 'finished'

		log.debug("Game concluded")

		return [ player.result for player in game.players ]

	def worker(self, game, transceiver):

		name = "(%d %s)" % (transceiver._i, transceiver._role)

		log.debug("%s worker started" % name)

		try:
			transceiver._start()

			i = 0
			while not game.should_finish():

				transceiver._recv(timeout=game.update_interval)

				log.debug("%s status update (%d)" % (name, i))

				status = game.get_status(transceiver._i, transceiver._role)

				transceiver._status_update(status)

				i += 1

		except StopGame:
			pass

		log.debug("%s worker stopped" % name)
		game.state = 'stopping'
