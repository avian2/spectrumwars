import Queue
import threading
import time

class StopGame(Exception): pass

class Testbed(object):
	def get_radio_pair(self):

		rxradio = Radio()
		txradio = Radio()

		rxradio.neighbor = txradio
		txradio.neighbor = rxradio

		return rxradio, txradio

class RadioTimeout(Exception): pass

class Radio(object):
	def __init__(self):
		self.neighbor = None

		self.settings = None
		self.rx_queue = Queue.Queue()

	def send(self, data):
		if self.settings == self.neighbor.settings:
			self.neighbor.rx_queue.put(data)

	def set_configuration(self, frequency, power, bandwidth):
		self.settings = (frequency, power, bandwidth)

	def recv(self, timeout=1.):
		try:
			data = self.rx_queue.get(block=False)
		except Queue.Empty:
			raise RadioTimeout
		else:
			return data

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

		# clean up any remaining packets in queues
		for transceiver in transceivers:
			try:
				transceiver._recv()
			except StopGame:
				pass

		game.state = 'finished'

		return [ player.result for player in game.players ]

	def worker(self, game, transceiver):

		try:
			transceiver.start()

			for i in xrange(game.time_limit):
				transceiver._recv()

				status = GameStatus()
				transceiver.status_update(status)

				if game.state != 'running':
					break

		except StopGame:
			pass

		game.state = 'stopping'
