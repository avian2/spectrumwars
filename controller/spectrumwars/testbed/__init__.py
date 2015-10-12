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

import time
import struct

class TestbedError(Exception): pass
class RadioError(Exception): pass
class RadioTimeout(Exception): pass

class TestbedBase(object):
	def get_radio_pair(self):
		raise NotImplementedError

	def time(self):
		return time.time()

	def start(self):
		pass

	def stop(self):
		pass

	def get_spectrum(self):
		raise NotImplementedError

	def get_packet_size(self):
		return self.RADIO_CLASS._get_packet_size()

	def get_frequency_range(self):
		raise NotImplementedError

	def get_bandwidth_range(self):
		raise NotImplementedError

	def get_power_range(self):
		raise NotImplementedError

class RadioBase(object):

	def __init__(self):
		self.lentype, self.lenbytes = self._get_lentype()

	def _add_header(self, data, payload):

		l = len(data)

		assert l <= self._get_packet_size()

		bindata =	struct.pack(self.lentype, l) + \
				data

		if payload:
			bindata += '\x00' * (self.PACKET_SIZE - self.lenbytes - l)
			assert len(bindata) == self.PACKET_SIZE

		return bindata

	def _del_header(self, bindata):

		assert len(bindata) >= self.lenbytes

		l = struct.unpack(self.lentype, bindata[:self.lenbytes])[0]

		return bindata[self.lenbytes:self.lenbytes + l]

	@classmethod
	def _get_packet_size(cls):
		lentype, lenbytes = cls._get_lentype()
		return cls.PACKET_SIZE - lenbytes

	@classmethod
	def _get_lentype(cls):
		if cls.PACKET_SIZE < 2**8:
			return 'B', 1
		elif cls.PACKET_SIZE < 2**16:
			return 'H', 2
		else:
			raise NotImplementedError

	def send(self, data, payload):
		if data is None:
			data = ''

		bindata = self._add_header(data, payload)
		self.binsend(bindata)

	def binsend(self, bindata):
		pass

	def recv(self, timeout=None):
		bindata = self.binrecv(timeout)
		data = self._del_header(bindata)

		return RadioPacket(data)

	def binrecv(self, timeout=None):
		raise NotImplementedError

	def set_configuration(self, frequency, power, bandwidth):
		pass

class RadioPacket(object):
	def __init__(self, data):
		self.data = data

	def to_json(self):
		d = [ ord(c) for c in self.data ]
		return (d,)

	@classmethod
	def from_json(cls, json):

		d = json[0]
		data = ''.join(chr(c) for c in d)

		return cls(data)

class GameStatus(object):
	def __init__(self, spectrum):
		self.spectrum = spectrum

	def to_json(self):
		return (self.spectrum,)

	@classmethod
	def from_json(cls, json):
		return cls(*json)
