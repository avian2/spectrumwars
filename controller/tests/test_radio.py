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

from itertools import combinations
import serial
import unittest

from spectrumwars.testbed import RadioError, RadioTimeout
from spectrumwars.testbed.vesna import RadioRaw as AsyncRadio
from spectrumwars.testbed.vesna import list_radio_devices

class SyncRadio(object):
	def __init__(self, device):
		self.device = device
		self.comm = serial.Serial(device, 115200, timeout=2.)

	def cmd(self, cmd):
		self.comm.write("%s\n" % (cmd,))

		while True:
			resp = self.comm.readline()
			if not resp:
				raise RadioTimeout("timeout waiting for response to %r" % (cmd,))
			elif resp == "O\n":
				break
			elif resp.startswith("E ") and resp.endswith("\n"):
				raise RadioError(resp[2:-1])
			else:
				self.debug(resp.strip())

	def recv(self):
		while True:
			resp = self.comm.readline()
			if not resp:
				raise RadioTimeout("timeout waiting for reception")
			elif resp.startswith("R "):
				return resp.strip()
			else:
				self.debug(resp.strip())

	def recv_flush(self):
		try:
			while True:
				self.recv()
		except RadioTimeout:
			pass

	def debug(self, msg):
		#print "%s >>> %s" % (self.device, msg)
		pass

	def start(self):
		pass

	def stop(self):
		pass


class OnLineRadioTestCase(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		l = list_radio_devices()

		if len(l) < 2:
			raise unittest.SkipTest("less than two VESNA nodes connected")

		cls.node1 = cls.RADIO_CLASS(l.pop())
		cls.node2 = cls.RADIO_CLASS(l.pop())

		cls.node1.start()
		cls.node2.start()

	@classmethod
	def tearDownClass(cls):
		cls.node1.stop()
		cls.node2.stop()

class TestRadioInterface(OnLineRadioTestCase):

	RADIO_CLASS = SyncRadio

	def test_set_address(self):
		self.node2.cmd("a 00")

	def test_invalid_cmd(self):
		self.assertRaisesRegexp(RadioError, "unknown command", self.node1.cmd, "x")

	def test_send_invalid_1(self):
		self.assertRaises(RadioError, self.node1.cmd, "t 02 0123456789abcde")

	def test_send_invalid_2(self):
		self.assertRaises(RadioError, self.node1.cmd, "t 02 0x23456789abcde")

	def test_send_invalid_3(self):
		self.assertRaises(RadioError, self.node1.cmd, "t 02 " + "01" * 254)

	def test_config_invalid_1(self):
		self.assertRaises(RadioError, self.node1.cmd, "c 300 0 0")

	def test_config_invalid_2(self):
		self.assertRaises(RadioError, self.node1.cmd, "c 0 5 0")

	def test_config_invalid_3(self):
		self.assertRaises(RadioError, self.node1.cmd, "c 0 5 17")

class TestRadio(OnLineRadioTestCase):

	RADIO_CLASS = SyncRadio

	def setUp(self):
		self.node1.cmd("a 01")
		self.node2.cmd("a 02")
		self.node1.cmd("c 0 0 0")
		self.node2.cmd("c 0 0 0")

	def tearDown(self):
		self.node1.cmd("a 00")
		self.node2.cmd("a 00")

	def test_send_one(self):
		self._send_one()

	def test_set_address(self):
		self.node2.cmd("a 03")
		self.assertRaises(RadioTimeout, self._send_one)

	def test_set_channel(self):
		self.node2.cmd("c 1 0 0")
		self.assertRaises(RadioTimeout, self._send_one)

	def _send_one(self, addr=2, n=20):
		data = "cd" * n
		self.node1.cmd("t %x %s" % (addr, data))
		expected = "R %s" % (data,)

		resp = self.node2.recv()
		self.assertEqual(resp, expected)

	def test_length(self):
		for bw in xrange(4):
			self.node1.cmd("c 0 %x 0" % (bw,))
			self.node2.cmd("c 0 %x 0" % (bw,))
			for n in xrange(1, 253, 10):
				#print bw, n
				self._send_one(n=n)

	def test_short(self):
		for bw in xrange(4):
			self.node1.cmd("c 0 %x 0" % (bw,))
			self.node2.cmd("c 0 %x 0" % (bw,))
			self._send_one(n=1)

	def test_send_min_len(self):
		self._send_one(n=1)

	def test_send_max_len(self):
		self._send_one(n=252)

	def off_test_send_many(self):
		for n in xrange(1000):
			self._send_one()

	def test_send_collision(self):
		for n in xrange(50):
			self.node1.cmd("t 02 " + "ab" * 10)
			self.node2.cmd("t 01 " + "ab" * 10)

		self.node1.recv_flush()
		self.node2.recv_flush()

	def test_config_1(self):
		for chan in xrange(0, 255, 50):
			for bw in xrange(4):
				self.node1.cmd("c %x %x 0" % (chan, bw))
				self.node2.cmd("c %x %x 0" % (chan, bw))
				self._send_one()

	def test_set_bitrate(self):
		self.node1.cmd("c 0 1 0")
		self.assertRaises(RadioTimeout, self._send_one)

class TestAsyncRadio(OnLineRadioTestCase):

	RADIO_CLASS = AsyncRadio

	def setUp(self):
		self.node1.cmd("a 01")
		self.node2.cmd("a 02")
		self.node1.cmd("c 0 0 0")
		self.node2.cmd("c 0 0 0")

	def tearDown(self):
		self.node1.cmd("a 00")
		self.node2.cmd("a 00")

	def test_long_null_packet(self):
		# this fails if data whitening isn't working
		data = "00" * 252
		N = 10

		for n in xrange(N):
			self.node1.cmd("t 2 %s" % (data,))

		expected = "R %s" % (data,)
		for n in xrange(N):
			resp = self.node2.recv()
			self.assertEqual(resp, expected)

	def test_fast_change_channel(self):
		data = "42"
		N = 10

		for n in xrange(N):
			self.node1.cmd("t 2 %s" % (data,))
			self.node1.cmd("c 1 0 0")
			self.node1.cmd("t 2 12")
			self.node1.cmd("c 0 0 0")

		expected = "R %s" % (data,)
		n = 0
		while True:
			try:
				resp = self.node2.recv()
			except RadioTimeout:
				break

			self.assertEqual(resp, expected)
			n += 1

		self.assertEqual(n, N)

class TestRadioCombinations(unittest.TestCase):

	def test_combinations(self):

		nodes = []
		for device in list_radio_devices():
			nodes.append(AsyncRadio(device))

		for node in nodes:
			node.start()

		for node1, node2 in combinations(nodes, 2):
			self._send_one(node1, node2)
			self._send_one(node2, node1)

		for node in nodes:
			node.stop()

	def _send_one(self, node1, node2):
		print node1.device, '->', node2.device

		npkt = 20

		for bitrate in xrange(4):
			nrcv = self._send(node1, node2, npkt=npkt, bitrate=bitrate)
			loss = float(npkt-nrcv) / npkt

			self.assertLess(loss, .1)

			print "bitrate=%d: %.1f%% packet loss" % (bitrate, loss*100.)

	def _send(self, node1, node2, len=100, npkt=1, bitrate=0):
		node1.cmd("a 41")
		node1.cmd("c a %d 0" % (bitrate,))
		node2.cmd("a 42")
		node2.cmd("c a %d 0" % (bitrate,))

		data = "cd" * len

		nrcv = 0
		for n in xrange(npkt):
			node1.cmd("t 42 %s" % (data,))

		for n in xrange(npkt):
			expected = "R %s" % (data,)

			try:
				resp = node2.recv(timeout=.1)
			except RadioTimeout:
				pass
			else:
				self.assertEqual(resp, expected)
				nrcv += 1

		node1.cmd("a 0")
		node2.cmd("a 0")

		return nrcv

if __name__ == "__main__":
	unittest.main()
