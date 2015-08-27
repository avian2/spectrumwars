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
