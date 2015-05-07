from gnuradio import blocks
from gnuradio import gr
from gnuradio import uhd
from gnuradio import fft
from gnuradio.fft import window
import specest
import time
from math import log10

class SpectrumSensor:
	def __init__(self):
		self.fft_size = 64

	        self.samp_rate = 6.4e6

		self.time_window = 200e-3 # s

	def start(self):
		self.setup_top_block()
		self.tb.start()

	def stop(self):
		self.tb.stop()
		self.tb.wait()

	def get_spectrum(self):
		x = self.probe_signal.level()
		return tuple(10.*log10(v) for v in x)

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

def main():

	s = SpectrumSensor()
	s.start()

	for i in xrange(60):
		time.sleep(1)
		print s.get_spectrum()

	s.stop()

if __name__ == "__main__":
	main()
