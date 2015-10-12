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

from gnuradio import blocks
from gnuradio import gr
from gnuradio import uhd
from gnuradio import fft
from gnuradio.fft import window
import specest
import time
from math import log10

class SpectrumSensor:
	def __init__(self, base_hz, step_hz, nchannels, time_window=200e-3, gain=10):

		self.samp_rate = step_hz*nchannels
		self.fft_size = nchannels
		self.center_freq = base_hz + self.samp_rate/2.

		self.time_window = time_window # s
		self.gain = gain

	def start(self):
		self.setup_top_block()
		self.tb.start()

	def stop(self):
		self.tb.stop()
		self.tb.wait()

	def get_spectrum(self):
		x = self.probe_signal.level()

		try:
			return tuple(10.*log10(v) for v in x)
		except ValueError:
			return tuple([0] * len(x))

	def setup_top_block(self):
		self.tb = gr.top_block()

		uhd_usrp_source = uhd.usrp_source(
			'',
			uhd.stream_args(
				cpu_format="fc32",
				channels=range(1),
			),
		)
		uhd_usrp_source.set_samp_rate(self.samp_rate)
		uhd_usrp_source.set_center_freq(self.center_freq, 0)
		uhd_usrp_source.set_gain(self.gain, 0)

		blocks_stream_to_vector = blocks.stream_to_vector(gr.sizeof_gr_complex, self.fft_size)

		fft_vxx = fft.fft_vcc(self.fft_size, True, (window.blackmanharris(self.fft_size)), True, 1)

		blocks_complex_to_mag_squared = blocks.complex_to_mag_squared(self.fft_size)

		avg_size = int(self.samp_rate / self.fft_size * self.time_window)
		specest_moving_average_vff = specest.moving_average_vff(avg_size, self.fft_size, 1./avg_size, 4096)

		self.probe_signal = blocks.probe_signal_vf(self.fft_size)

		self.tb.connect((uhd_usrp_source, 0), (blocks_stream_to_vector, 0))
		self.tb.connect((blocks_stream_to_vector, 0), (fft_vxx, 0))
		self.tb.connect((fft_vxx, 0), (blocks_complex_to_mag_squared, 0))
		self.tb.connect((blocks_complex_to_mag_squared, 0), (specest_moving_average_vff, 0))
		self.tb.connect((specest_moving_average_vff, 0), (self.probe_signal, 0))
