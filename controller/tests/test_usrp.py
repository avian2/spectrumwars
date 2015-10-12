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
