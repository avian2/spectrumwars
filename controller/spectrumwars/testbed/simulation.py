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
import Queue
import random
import time

from spectrumwars.testbed import TestbedBase, RadioBase, RadioTimeout, RadioError, TestbedError, RadioPacket

log = logging.getLogger(__name__)

class Radio(RadioBase):
	RECEIVE_TIMEOUT = 2.

	def __init__(self, addr, dispatcher, send_delay):
		super(Radio, self).__init__()

		self.addr = addr
		self.neighbor = None
		self.dispatcher = dispatcher
		self.q = Queue.Queue()

		self.frequency = 0
		self.bandwidth = 0

		self.send_delay = send_delay

	def _recv(self, addr, bindata, frequency, bandwidth):
		if self.frequency == frequency and self.bandwidth == bandwidth and self.addr == addr:
			self.q.put(bindata)

	def set_configuration(self, frequency, bandwidth, power):
		self.frequency = frequency
		self.bandwidth = bandwidth

	def binsend(self, bindata):
		self.dispatcher(self.neighbor, bindata, self.frequency, self.bandwidth)
		time.sleep(self.send_delay)

	def binrecv(self, timeout=None):
		if timeout is None:
			timeout = self.RECEIVE_TIMEOUT

		try:
			bindata = self.q.get(True, timeout)
		except Queue.Empty:
			raise RadioTimeout
		else:
			return bindata

class Testbed(TestbedBase):

	RADIO_CLASS = Radio

	def __init__(self, send_delay=.1, frequency_range=64, bandwidth_range=10, power_range=10, packet_size=1024):
		self.send_delay = float(send_delay)
		self.frequency_range = int(frequency_range)
		self.bandwidth_range = int(bandwidth_range)
		self.power_range = int(power_range)

		self.RADIO_CLASS.PACKET_SIZE = int(packet_size) + 1

		self.radios = []

		# for each channel, we keep the timestamp of the last
		# transmission. we use this for simulated spectrum sensing and
		# for detecting collisions.
		self.channels = [0] * self.frequency_range

		self.i = 0

	def _get_radio(self):
		r = Radio(self.i, self._dispatcher, self.send_delay)
		self.radios.append(r)

		self.i += 1

		return r

	def _dispatcher(self, addr, bindata, frequency, bandwidth):
		now = self.time()

		has_collision = (now - self.channels[frequency]) > self.send_delay
		self.channels[frequency] = now

		if has_collision:
			# note that when packets collide, the first one goes
			# through while the later ones fail. this is different
			# than in reality: all should fail. But this would
			# be complicated to implement in practice.
			for radio in self.radios:
				radio._recv(addr, bindata, frequency, bandwidth)
		else:
			log.debug("packet collision detected on channel %d" % (frequency,))

	def get_radio_pair(self):
		dst = self._get_radio()
		src = self._get_radio()

		dst.neighbor = src.addr
		src.neighbor = dst.addr

		return dst, src

	def get_spectrum(self):

		spectrum = []
		now = self.time()

		for time in self.channels:
			if now - time < .5:
				p = random.randint(-40, -20)
			else:
				p = random.randint(-90, -80)

			spectrum.append(p)

		return tuple(spectrum)

	def get_frequency_range(self):
		return self.frequency_range

	def get_bandwidth_range(self):
		return self.bandwidth_range

	def get_power_range(self):
		return self.power_range
