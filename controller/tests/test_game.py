# Copyright (C) 2015 SensorLab, Jozef Stefan Institute http://sensorlab.ijs.si
#
# Written by Tomaz Solc, tomaz.solc@ijs.si
#
# This work has been partially funded by the European Community through the
# 7th Framework Programme project CREW (FP7-ICT-2009-258301).
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see http://www.gnu.org/licenses/

import logging
import unittest
import threading

import Queue
from spectrumwars import Transceiver, Player, Game, GameController, RadioTimeout, RadioError
from spectrumwars.testbed import TestbedBase, RadioBase, RadioPacket
from spectrumwars.sandbox.threaded import ThreadedSandbox

level = logging.WARNING
logging.basicConfig(level=level)

def log_exc_off():
	logging.getLogger().setLevel(logging.ERROR)

def log_exc_on():
	logging.getLogger().setLevel(level)


class MockRadio(RadioBase):
	PACKET_SIZE = 201

	def __init__(self, testbed):
		super(MockRadio, self).__init__()

		self.testbed = testbed
		self.neighbor = None

		self.settings = None
		self.rx_queue = Queue.Queue()

	def binsend(self, data):
		if self.settings == self.neighbor.settings:
			self.neighbor.rx_queue.put(data)

	def set_configuration(self, frequency, power, bandwidth):
		self.settings = (frequency, power, bandwidth)

	def get_configuration(self):
		return self.settings

	def binrecv(self, timeout=None):
		try:
			data = self.rx_queue.get(timeout=.01)
		except Queue.Empty:
			self.testbed.clock += timeout
			raise RadioTimeout
		else:
			return data

class MockTestbed(TestbedBase):
	RADIO_CLASS = MockRadio

	def get_radio_pair(self):

		dst_radio = MockRadio(self)
		src_radio = MockRadio(self)

		dst_radio.neighbor = src_radio
		src_radio.neighbor = dst_radio

		self.clock = 0.

		return dst_radio, src_radio

	def time(self):
		return self.clock

	def get_spectrum(self):
		return True

	def get_frequency_range(self):
		return 10

	def get_bandwidth_range(self):
		return 11

	def get_power_range(self):
		return 12


class TestGame(unittest.TestCase):

	PACKET_LIMIT = 50
	TIME_LIMIT = 50
	PAYLOAD_LIMIT = 200*10

	def setUp(self):
		self.testbed = MockTestbed()

	def _run_game(self, dst_cls, src_cls, packet_limit=PACKET_LIMIT, payload_limit=PAYLOAD_LIMIT,
			time_limit=TIME_LIMIT):

		sandbox = ThreadedSandbox([[dst_cls, src_cls]])
		game = Game(self.testbed, sandbox,
				packet_limit=packet_limit,
				time_limit=time_limit,
				payload_limit=payload_limit)
		ctl = GameController()
		return ctl.run(game)[0]

	def test_timeout(self):

		class Destination(Transceiver):
			pass

		class Source(Transceiver):
			pass

		result = self._run_game(Destination, Source)
		self.assertEqual(result.dst_received_packets, 0)
		self.assertEqual(result.src_received_packets, 0)
		self.assertEqual(result.dst_transmit_packets, 0)
		self.assertEqual(result.src_transmit_packets, 0)

	def test_one_packet(self):

		class Destination(Transceiver):
			def start(self):
				self.set_configuration(0, 0, 0)

		class Source(Transceiver):
			def start(self):
				self.set_configuration(0, 0, 0)
				self.send()

		result = self._run_game(Destination, Source)
		self.assertEqual(result.dst_received_packets, 1)
		self.assertEqual(result.src_received_packets, 0)
		self.assertEqual(result.dst_transmit_packets, 0)
		self.assertEqual(result.src_transmit_packets, 1)
		self.assertEqual(result.payload_bytes, self.testbed.get_packet_size())

	def test_one_packet_reverse(self):

		class Destination(Transceiver):
			def start(self):
				self.send()

		result = self._run_game(Destination, Transceiver)
		self.assertEqual(result.dst_received_packets, 0)
		self.assertEqual(result.src_received_packets, 1)
		self.assertEqual(result.dst_transmit_packets, 1)
		self.assertEqual(result.src_transmit_packets, 0)
		self.assertEqual(result.payload_bytes, 0)

	def test_one_packet_miss(self):

		class Destination(Transceiver):
			def start(self):
				self.set_configuration(0, 0, 0)

		class Source(Transceiver):
			def start(self):
				self.set_configuration(1, 0, 0)
				self.send()

		result = self._run_game(Destination, Source)
		self.assertEqual(result.dst_received_packets, 0)
		self.assertEqual(result.src_received_packets, 0)
		self.assertEqual(result.dst_transmit_packets, 0)
		self.assertEqual(result.src_transmit_packets, 1)

	def test_all_packets(self):

		class Destination(Transceiver):
			def start(self):
				self.set_configuration(0, 0, 0)

		class Source(Transceiver):
			def start(self):
				self.set_configuration(0, 0, 0)

				while True:
					self.send()

		result = self._run_game(Destination, Source, payload_limit=None, time_limit=None)
		self.assertGreaterEqual(result.dst_received_packets, self.PACKET_LIMIT)

	def test_all_payload(self):

		class Source(Transceiver):
			def start(self):
				while True:
					self.send()

		result = self._run_game(Transceiver, Source, packet_limit=None, time_limit=None)
		self.assertGreaterEqual(result.payload_bytes, self.PAYLOAD_LIMIT)

	def test_recv_packet(self):

		cnt = [0]

		class Destination(Transceiver):
			def start(self):
				self.set_configuration(0, 0, 0)

			def recv(self, packet):
				cnt[0] += 1

		class Source(Transceiver):
			def start(self):
				self.set_configuration(0, 0, 0)
				self.send()

		result = self._run_game(Destination, Source)
		self.assertEqual(cnt[0], 1)

	def test_dst_starts_after_src(self):
		# This is mostly to test that our MockRadio and MockTestbed
		# operate deterministically.
		#
		# Since we're not doing any real time.sleep(), it might happen
		# that destination event loop only starts running after source
		# has already triggered end game condition.

		lock = threading.Lock()
		lock.acquire()

		class Destination(Transceiver):
			def start(self):
				lock.acquire()

		class Source(Transceiver):
			def start(self):
				self.send()

			def _stop(self):
				lock.release()

		result = self._run_game(Destination, Source)
		self.assertEqual(result.dst_received_packets, 1)

	def test_recv_packet_data(self):

		cnt = [0]
		foo = "foo"

		class Destination(Transceiver):
			def start(self):
				self.set_configuration(0, 0, 0)

			def recv(self, packet):
				cnt[0] = packet

		class Source(Transceiver):
			def start(self):
				self.set_configuration(0, 0, 0)
				self.send(foo)

		result = self._run_game(Destination, Source)
		self.assertEqual(cnt[0].data, foo)
		self.assertEqual(result.payload_bytes, self.testbed.get_packet_size() - len(foo))

	def test_max_length_packet_data(self):

		cnt = [0]
		foo = "x" * self.testbed.get_packet_size()

		class Destination(Transceiver):
			def recv(self, packet):
				cnt[0] = packet

		class Source(Transceiver):
			def start(self):
				self.send(foo)

		result = self._run_game(Destination, Source)
		self.assertEqual(cnt[0].data, foo)
		self.assertEqual(result.payload_bytes, 0)

	def test_too_long_packet_data(self):

		foo = "x" * (self.testbed.get_packet_size() + 1)

		class Source(Transceiver):
			def start(self):
				self.send(foo)


		log_exc_off()
		result = self._run_game(Transceiver, Source)
		log_exc_on()
		self.assertTrue(result.crashed)

	def test_status(self):

		cnt = [0]

		class Destination(Transceiver):
			def status_update(self, status):
				cnt[0] += 1

		result = self._run_game(Destination, Transceiver)
		self.assertGreater(cnt[0], 1)
		#self.assertEqual(cnt[0], self.TIME_LIMIT)

	def test_get_packet_size(self):

		cnt = [0]

		class Destination(Transceiver):
			def start(self):
				cnt[0] = self.get_packet_size()

		result = self._run_game(Destination, Transceiver)
		self.assertEqual(cnt[0], self.testbed.get_packet_size())

	def test_error_recv(self):

		class Destination(Transceiver):
			def recv(self, packet):
				raise Exception

		class Source(Transceiver):
			def start(self):
				while True:
					self.send()

		log_exc_off()
		result = self._run_game(Destination, Source)
		log_exc_on()
		self.assertEqual(result.crashed, True)
		self.assertEqual(len(result.crash_report), 1)
		self.assertTrue("Traceback" in result.crash_report[0])
		self.assertTrue("Destination" in result.crash_report[0])
		self.assertTrue("Source" not in result.crash_report[0])

	def test_error_start(self):

		class Destination(Transceiver):
			def start(self):
				raise Exception

		log_exc_off()
		result = self._run_game(Destination, Transceiver)
		log_exc_on()
		self.assertEqual(result.crashed, True)
		self.assertEqual(len(result.crash_report), 1)
		self.assertTrue("Traceback" in result.crash_report[0])
		self.assertTrue("Destination" in result.crash_report[0])
		self.assertTrue("Source" not in result.crash_report[0])

	def test_error_status_update(self):

		class Destination(Transceiver):
			def status_update(self, status):
				raise Exception

		log_exc_off()
		result = self._run_game(Destination, Transceiver)
		log_exc_on()
		self.assertEqual(result.crashed, True)
		self.assertEqual(len(result.crash_report), 1)
		self.assertTrue("Traceback" in result.crash_report[0])
		self.assertTrue("Destination" in result.crash_report[0])
		self.assertTrue("Source" not in result.crash_report[0])

	def test_recv_in_start(self):

		cnt = [0, 0, 0]

		class Destination(Transceiver):
			def start(self):
				for data in self.recv_loop(timeout=2.):
					cnt[1] += 1

			def recv(self, packet):
				cnt[0] += 1

		class Source(Transceiver):
			def start(self):
				while True:
					cnt[2] += 1
					self.send()

		result = self._run_game(Destination, Source, payload_limit=None, time_limit=None)

		self.assertEqual(result.crashed, False)
		self.assertGreaterEqual(cnt[0], self.PACKET_LIMIT)
		self.assertGreaterEqual(cnt[1], self.PACKET_LIMIT)
		self.assertGreaterEqual(cnt[2], self.PACKET_LIMIT)

	def test_status_update(self):

		sl = []

		class Destination(Transceiver):
			def status_update(self, status):
				sl.append(status)

		self._run_game(Destination, Transceiver)

		for s in sl:
			self.assertTrue(s.spectrum)

	def test_get_configuration(self):
		sl = []

		class Destination(Transceiver):
			def start(self):
				self.set_configuration(0, 1, 2)
				sl.append(self.get_configuration())

		self._run_game(Destination, Transceiver)
		self.assertEqual([0, 1, 2], sl[0])

	def test_get_frequency_range(self):
		sl = []

		class Destination(Transceiver):
			def start(self):
				sl.append(self.get_frequency_range())

		self._run_game(Destination, Transceiver)
		self.assertEqual(10, sl[0])

	def test_get_bandwidth_range(self):
		sl = []

		class Destination(Transceiver):
			def start(self):
				sl.append(self.get_bandwidth_range())

		self._run_game(Destination, Transceiver)
		self.assertEqual(11, sl[0])

	def test_get_power_range(self):
		sl = []

		class Destination(Transceiver):
			def start(self):
				sl.append(self.get_power_range())

		self._run_game(Destination, Transceiver)
		self.assertEqual(12, sl[0])

	def test_set_configuration_error(self):
		cnt = [0]

		class Destination(Transceiver):
			def start(self):
				try:
					self.set_configuration(self.get_frequency_range(), 0, 0)
				except RadioError:
					cnt[0] += 1

		self._run_game(Destination, Transceiver)
		self.assertEqual(cnt[0], 1)

from spectrumwars.game import GameRPCServer

class TestGameRPCServer(unittest.TestCase):
	def test_get_endpoint(self):
		endpoint = GameRPCServer.get_endpoint(0, 'tx')
		self.assertEqual(endpoint, "tcp://127.0.0.1:50000")

if __name__ == '__main__':
	unittest.main()
