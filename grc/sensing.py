from gnuradio import blocks
from gnuradio import gr
from gnuradio import uhd
from gnuradio import fft
from gnuradio.fft import window
import specest
import time

class SpectrumSensor:
	def __init__(self):
		self.vec_size = 64
	        self.samp_rate = 5e6

	def start(self):
		self.setup_top_block()
		self.tb.start()

	def stop(self):
		self.tb.stop()
		self.tb.wait()

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
		uhd_usrp_source.set_center_freq(2400e6 + self.samp_rate/2., 0)
		uhd_usrp_source.set_gain(10, 0)

		blocks_stream_to_vector = blocks.stream_to_vector(gr.sizeof_gr_complex*1, self.vec_size)

		fft_vxx = fft.fft_vcc(self.vec_size, True, (window.blackmanharris(self.vec_size)), True, 1)

		blocks_complex_to_mag_squared = blocks.complex_to_mag_squared(self.vec_size)

		specest_moving_average_vff = specest.moving_average_vff(20000, self.vec_size, 1./200000., 4096)

		blocks_nlog10_ff = blocks.nlog10_ff(10, self.vec_size, 0)

		self.probe_signal = blocks.probe_signal_vf(self.vec_size)

		self.tb.connect((uhd_usrp_source, 0), (blocks_stream_to_vector, 0))
		self.tb.connect((blocks_stream_to_vector, 0), (fft_vxx, 0))
		self.tb.connect((fft_vxx, 0), (blocks_complex_to_mag_squared, 0))
		self.tb.connect((blocks_complex_to_mag_squared, 0), (specest_moving_average_vff, 0))
		self.tb.connect((specest_moving_average_vff, 0), (blocks_nlog10_ff, 0))
		self.tb.connect((blocks_nlog10_ff, 0), (self.probe_signal, 0))

def main():

	s = SpectrumSensor()
	s.start()

	for i in xrange(60):
		time.sleep(1)
		print s.probe_signal.level()

	s.stop()

main()
