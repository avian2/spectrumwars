import unittest
import time
from spectrumwars.testbed.usrp_sensing import SpectrumSensor

class TestUSRP(unittest.TestCase):
	def test_constructor(self):
		ss = SpectrumSensor(base_hz=2.4e9, step_hz=100e3, nchannels=64)

		self.assertEqual(ss.center_freq, 2.4032e9)
		self.assertEqual(ss.samp_rate, 6.4e6)
		self.assertEqual(ss.fft_size, 64)

class TestUSRPLive(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.ss = SpectrumSensor(base_hz=2.4e9, step_hz=100e3, nchannels=64)

		try:
			cls.ss.start()
		except RuntimeError, e:
			if 'No devices found' in str(e):
				raise unittest.SkipTest("USRP not connected")
			else:
				raise

	@classmethod
	def tearDownClass(cls):
		cls.ss.stop()

	def test_basic(self):
		time.sleep(.1)
		s = self.ss.get_spectrum()

		self.assertLess(max(s), -10)
		self.assertGreater(min(s), -100)
