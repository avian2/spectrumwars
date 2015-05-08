import unittest
import time
from spectrumwars.testbed.usrp_sensing import SpectrumSensor

class TestUSRP(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.ss = SpectrumSensor()

		try:
			cls.ss.start()
		except RuntimeError, e:
			if 'No devices found' in str(e):
				raise unittest.SkipTest("USRP not connected")

	@classmethod
	def tearDownClass(cls):
		cls.ss.stop()

	def test_basic(self):
		time.sleep(.1)
		s = self.ss.get_spectrum()

		self.assertLess(max(s), -10)
		self.assertGreater(min(s), -100)
