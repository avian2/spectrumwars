import copy
import logging
import time
from spectrumwars.testbed import TestbedError, RadioTimeout, GameStatus
from spectrumwars.transceiver import StopGame, TransceiverError
from jsonrpc2_zeromq import RPCServer

log = logging.getLogger(__name__)

class PlayerInstance(object):
	def __init__(self, transceiver, server):
		self.transceiver = transceiver
		self.server = server

class Player(object):
	def __init__(self, sb_player, game):

		self.i = sb_player.i
		self.game = game

		self.result = PlayerResult()
		self.instances = []

		rxradio, txradio = game.testbed.get_radio_pair()

		for radio, transceiver in zip((rxradio, txradio), (sb_player.rx, sb_player.tx)):
			transceiver.init(self.i, game.update_interval)
			server = GameRPCServer(game, self, transceiver.role, radio)
			server.start()

			instance = PlayerInstance(transceiver, server)
			self.instances.append(instance)

	def start(self):
		for instance in self.instances:
			instance.transceiver.start(instance.server.endpoint)

	def join(self):
		if self.game.hard_time_limit is None:
			deadline = None
		else:
			deadline = self.game.start_time + self.game.hard_time_limit
		for instance in self.instances:
			instance.transceiver.join(deadline, timefunc=self.game.testbed.time)

			instance.server.stop()
			instance.server.join()

		self.instances = []

class PlayerResult(object):
	def __init__(self):
		# number of received packets in both directions
		self.received_packets = 0
		# number of transmitted packets in both directions
		self.transmit_packets = 0
		# whether the player's code raised an unhandled exception
		self.crashed = False
		# list of reasons why the player's code crashed
		self.crash_desc = []
		# number of bytes transferred from transmitter to receiver
		self.payload_bytes = 0

class Game(object):

	def __init__(self, testbed, sandbox, packet_limit=100, time_limit=None, payload_limit=None):
		self.testbed = testbed
		self.sandbox = sandbox
		self.packet_limit = packet_limit
		self.soft_time_limit = time_limit
		self.hard_time_limit = time_limit + 10 if time_limit is not None else None
		self.payload_limit = payload_limit

		self.update_interval = 1
		self.start_time = None
		self.end_time = None

		self.state = 'new'

		self.log = []

	def should_finish(self):

		if self.soft_time_limit is not None:
			if self.testbed.time() - self.start_time > self.soft_time_limit:
				log.debug("game time limit reached!")
				return True

		for player in self.players:
			if self.packet_limit is not None:
				if player.result.received_packets >= self.packet_limit:
					log.debug("game packet limit reached by player %d!" %
							player.i)
					return True
			if self.payload_limit is not None:
				if player.result.payload_bytes >= self.payload_limit:
					log.debug("game payload limit reached by player %d!" %
							player.i)
					return True

		if self.state != 'running':
			return True

		return False

	def instantiate(self):
		self.players = []
		for sb_player in self.sandbox.get_players():
			player = Player(sb_player, self)
			self.players.append(player)

	def log_event(self, type, **kwargs):
		event = GameEvent(type, **kwargs)
		event.timestamp = self.testbed.time()
		event.results = [ copy.copy(player.result) for player in self.players ]
		self.log.append(event)

	def get_status(self):
		status = GameStatus(self.testbed.get_spectrum())

		return status

class GameEvent(object):
	def __init__(self, type, **kwargs):
		self.type = type
		self.timestamp = None
		self.data = kwargs

class GameRPCServer(RPCServer):

	def __init__(self, game, player, role, radio):
		self.game = game
		self.player = player
		self.radio = radio

		self.i = player.i
		j = 1 if role == 'rx' else 0

		self.role = role
		self.xname = "(%d %s)" % (self.i, self.role)

		port = 50000 + self.i*10 + j
		self.endpoint = "tcp://127.0.0.1:%d" % (port,)

		RPCServer.__init__(self, self.endpoint, timeout=.5)

	def handle_get_status_method(self):
		status = self.game.get_status()
		self.game.log_event("status", i=self.i, role=self.role, status=status)
		return status.to_json()

	def handle_send_method(self, data):
		self.game.log_event("send", i=self.i, role=self.role)
		self.player.result.transmit_packets += 1

		return self.radio.send(data)

	def handle_recv_method(self, timeout):
		try:
			packet = self.radio.recv(timeout)

			self.player.result.received_packets += 1

			if self.role == 'rx':
				payload_bytes = self.game.testbed.get_packet_size()
				if packet.data:
					payload_bytes -= len(packet.data)
				self.player.result.payload_bytes += payload_bytes

			self.game.log_event("recv",  i=self.i, role=self.role)

			return packet.to_json()

		except RadioTimeout:
			return None

	def handle_set_configuration_method(self, frequency, bandwidth, power):
		self.game.log_event("config", i=self.i, role=self.role,
				frequency=frequency, bandwidth=bandwidth, power=power)
		self.radio.set_configuration(frequency, bandwidth, power)

	def handle_get_packet_size_method(self):
		return self.game.testbed.get_packet_size()

	def handle_report_stop_method(self, crashed, crash_desc=None):
		if crashed:
			self.player.result.crashed = True
			self.player.result.crash_desc.append(crash_desc)

		self.game.state = 'stopping'

	def handle_should_finish_method(self):
		return self.game.should_finish()

class GameController(object):
	def __init__(self):
		pass

	def run(self, game):

		log.debug("Instantiating player classes")
		game.instantiate()
		game.testbed.start()

		game.state = 'running'

		game.start_time = game.testbed.time()

		for player in game.players:
			player.start()

		for player in game.players:
			player.join()

		game.end_time = game.testbed.time()

		log.debug("Cleaning up testbed")

		game.testbed.stop()
		game.state = 'finished'

		log.debug("Game concluded")

		return [ player.result for player in game.players ]
