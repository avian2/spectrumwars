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

from spectrumwars.testbed import TestbedBase, RadioBase

import unittest

class TestRadioBase(unittest.TestCase):

	def test_add_del_payload_8(self):

		class Radio(RadioBase):
			PACKET_SIZE = 100

		radio = Radio()
		self.assertEqual(radio._get_packet_size(), 99)

		d = radio._add_header("foo", True)
		data = radio._del_header(d)

		self.assertEqual(len(d), 100)
		self.assertEqual(data, "foo")

	def test_add_del_payload_16(self):

		class Radio(RadioBase):
			PACKET_SIZE = 1000

		radio = Radio()
		self.assertEqual(radio._get_packet_size(), 998)

		d = radio._add_header("foo", True)
		data = radio._del_header(d)

		self.assertEqual(len(d), 1000)
		self.assertEqual(data, "foo")

	def test_add_del_header_8(self):

		class Radio(RadioBase):
			PACKET_SIZE = 100

		radio = Radio()
		self.assertEqual(radio._get_packet_size(), 99)

		d = radio._add_header("foo", False)
		data = radio._del_header(d)

		self.assertEqual(len(d), 4)
		self.assertEqual(data, "foo")

	def test_add_del_header_16(self):

		class Radio(RadioBase):
			PACKET_SIZE = 1000

		radio = Radio()
		self.assertEqual(radio._get_packet_size(), 998)

		d = radio._add_header("foo", False)
		data = radio._del_header(d)

		self.assertEqual(len(d), 5)
		self.assertEqual(data, "foo")


class TestTestbedBase(unittest.TestCase):

	def test_get_packet_size(self):

		class Radio(RadioBase):
			PACKET_SIZE = 100

		class Testbed(TestbedBase):
			RADIO_CLASS = Radio

		testbed = Testbed()
		self.assertEqual(testbed.get_packet_size(), 99)
