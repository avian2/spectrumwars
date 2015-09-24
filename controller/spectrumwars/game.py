import copy
import logging
import time
import threading
from spectrumwars.testbed import TestbedError, RadioTimeout, RadioPacket, GameStatus
from spectrumwars.rpc import RPCServer

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

		dst_radio, src_radio = game.testbed.get_radio_pair()

		for radio, transceiver in zip((dst_radio, src_radio), (sb_player.dst, sb_player.src)):
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
		self.dst_received_packets = 0
		self.src_received_packets = 0
		# number of transmitted packets in both directions
		self.dst_transmit_packets = 0
		self.src_transmit_packets = 0
		# whether the player's code raised an unhandled exception
		self.crashed = False
		# list of reasons why the player's code crashed
		self.crash_report = []
		# number of bytes transferred from source to destination
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
				if player.result.dst_received_packets >= self.packet_limit:
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
		j = 1 if role == 'dst' else 0

		self.role = role
		self.xname = "(%d %s)" % (self.i, self.role)

		port = 50000 + self.i*10 + j
		self.endpoint = "tcp://127.0.0.1:%d" % (port,)

		super(GameRPCServer, self).__init__(self.endpoint, timeout=.5)

	def log_event(self, type, **kwargs):
		self.game.log_event(type, i=self.i, role=self.role, **kwargs)

	def handle_get_status_method(self):
		status = self.game.get_status()
		self.log_event("status", status=status)
		return status.to_json()

	def handle_send_method(self, packet_json):
		self.log_event("send")

		if self.role == 'src':
			self.player.result.src_transmit_packets += 1
			payload = True
		else:
			self.player.result.dst_transmit_packets += 1
			payload = False

		data = RadioPacket.from_json(packet_json).data
		return self.radio.send(data, payload)

	def handle_recv_method(self, timeout):
		try:
			packet = self.radio.recv(timeout)

			if self.role == 'dst':
				self.player.result.dst_received_packets += 1

				payload_bytes = self.game.testbed.get_packet_size()
				if packet.data:
					payload_bytes -= len(packet.data)
				self.player.result.payload_bytes += payload_bytes
			else:
				self.player.result.src_received_packets += 1

			self.log_event("recv")

			return packet.to_json()

		except RadioTimeout:
			return None

	def handle_set_configuration_method(self, frequency, bandwidth, power):
		self.log_event("config", frequency=frequency, bandwidth=bandwidth, power=power)
		self.radio.set_configuration(frequency, bandwidth, power)

	def handle_get_configuration_method(self):
		return self.radio.get_configuration()

	def handle_get_packet_size_method(self):
		return self.game.testbed.get_packet_size()

	def handle_get_ranges_method(self):
		ranges = (	self.game.testbed.get_frequency_range(),
				self.game.testbed.get_bandwidth_range(),
				self.game.testbed.get_power_range())
		return ranges

	def handle_report_stop_method(self, crashed, crash_report=None):
		if crashed:
			self.player.result.crashed = True

			if self.role == 'dst':
				header = "Destination crash report:\n\n"
			else:
				header = "Source crash report:\n\n"

			self.player.result.crash_report.append(header + crash_report)

		self.game.state = 'stopping'

	def handle_should_finish_method(self):
		return self.game.should_finish()

class SpectrumLogger(object):
	def __init__(self, game, update_interval):
		self.want_stop = False
		self.update_interval = update_interval
		self.game = game

	def start(self):
		self.thread = threading.Thread(target=self.work)
		self.thread.start()

	def work(self):
		while not self.want_stop:
			status = self.game.get_status()
			self.game.log_event("status", i=-1, role='log', status=status)
			time.sleep(self.update_interval)

	def stop(self):
		self.want_stop = True
		self.thread.join()

class GameController(object):
	def __init__(self):
		pass

	def run(self, game):

		log.debug("Instantiating player classes")
		game.instantiate()
		game.testbed.start()

		slogger = SpectrumLogger(game, game.update_interval/5.)
		slogger.start()

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

		slogger.stop()

		log.debug("Game concluded")

		return [ player.result for player in game.players ]
