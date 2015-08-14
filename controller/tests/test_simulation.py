import unittest

from spectrumwars import RadioTimeout
from spectrumwars.testbed.simulation import Testbed

class TestSimulation(unittest.TestCase):

	def setUp(self):
		self.t = Testbed()
		self.r1, self.r2 = self.t.get_radio_pair()

	def test_send(self):
		self.r1.set_configuration(0, 0, 0)
		self.r2.set_configuration(0, 0, 0)

		self.r1.send("foo")
		d = self.r2.recv()

		self.assertEqual(d.data, "foo")

	def test_send_self(self):
		self.r1.set_configuration(0, 0, 0)

		self.r1.send("foo")
		self.assertRaises(RadioTimeout, self.r1.recv)

	def test_send_invalid(self):
		self.r1.set_configuration(0, 0, 0)
		self.r2.set_configuration(1, 0, 0)

		self.r1.send("foo")
		self.assertRaises(RadioTimeout, self.r2.recv)

	def test_get_spectrum(self):
		s = self.t.get_spectrum()

		self.assertEqual(len(s), self.t.get_frequency_range())

