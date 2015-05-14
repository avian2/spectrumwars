import logging
import os
import serial
import threading
import time
import Queue

from spectrumwars.testbed import TestbedBase, RadioBase, RadioTimeout, RadioError, TestbedError
from spectrumwars.testbed.usrp_sensing import SpectrumSensor

log = logging.getLogger(__name__)

class RadioRaw(object):

	COMMAND_RESPONSE_TIMEOUT = .5
	RECEIVE_TIMEOUT = 2.
	STOP_POLL = .5

	def __init__(self, device):
		self.device = device
		self.comm = serial.Serial(device, 115200, timeout=self.STOP_POLL)

		self.rx_queue = Queue.Queue()

		self.command_lock = threading.Lock()
		self.response_event = threading.Event()
		self.response = None

	def start(self):
		self.run = True
		self.worker_thread = threading.Thread(target=self.worker)
		self.worker_thread.start()

	def stop(self):
		self.run = False
		self.worker_thread.join()

	def cmd(self, cmd):
		self.command_lock.acquire()

		self.response_event.clear()
		self.comm.write("%s\n" % (cmd,))

		if self.response_event.wait(self.COMMAND_RESPONSE_TIMEOUT):
			resp = self.response
		else:
			resp = None

		self.command_lock.release()

		if resp is None:
			raise RadioTimeout("%s: timeout waiting for response to %r" % (self.device, cmd))
		elif resp == "O":
			pass
		elif resp.startswith("E "):
			raise RadioError(resp[2:])
		else:
			print resp
			assert False

	def recv(self, timeout=None):
		if timeout is None:
			timeout = self.RECEIVE_TIMEOUT

		try:
			resp = self.rx_queue.get(timeout=timeout)
		except Queue.Empty:
			raise RadioTimeout("timeout waiting for reception")
		else:
			return resp.strip()

	def recv_flush(self):
		try:
			while True:
				self.rx_queue.get(block=False)
		except Queue.Empty:
			pass

	def debug(self, msg):
		log.debug("%s: radio debug: %s" % (self.device, msg))

	def worker(self):
		while self.run:
			resp = self.comm.readline()
			if not resp:
				continue
			elif resp.startswith("R "):
				self.rx_queue.put(resp.strip())
			elif resp.startswith("E ") or resp.startswith("O"):
				self.response = resp.strip()
				self.response_event.set()
			else:
				self.debug(resp.strip())

class Radio(RadioBase):

	DATA_LEN = 252
	CMD_RETRIES = 3

	def __init__(self, path, addr):

		self.raw = RadioRaw(path)
		self.addr = addr

		self.neighbor = None

	def start(self):
		self.raw.start()
		self._cmd("a %02x" % (self.addr,))
		self._cmd("c 0 0 0")

	def _cmd(self, cmd):
		for n in xrange(self.CMD_RETRIES):
			try:
				self.raw.cmd(cmd)
			except RadioTimeout:
				log.warning("Command timeout: %r" % (cmd,))
			except RadioError, e:
				log.warning("Command error: %r: %s" % (cmd, e))
			else:
				return

		log.error("Giving up on %r after %d errors" % (cmd, n+1))

	def send(self, data):

		if data is None:
			data = ''

		if len(data) > self.DATA_LEN - 1:
			data = data[:self.DATA_LEN-1]

		bindata =	[ len(data) ] + \
				[ ord(c) for c in data ] + \
				[ 0 ] * (self.DATA_LEN - 1 - len(data))

		assert len(bindata) == self.DATA_LEN

		strdata = ''.join(("%02x" % v) for v in bindata)

		self._cmd("t %02x %s" % (self.neighbor, strdata))

	def set_configuration(self, frequency, bandwidth, power):
		self._cmd("c %x %x %x" % (frequency, bandwidth, power))

	def recv(self, timeout=1.):
		data = self.raw.recv(timeout=timeout)

		assert data.startswith("R ")

		strdata = data[2:]

		# NOTE: have seen this fail in clean-up
		assert len(strdata) == self.DATA_LEN*2

		n = int(strdata[0:2], 16)
		assert n <= self.DATA_LEN - 1

		bindata = []

		for i in xrange(1, n+1):
			bindata.append(chr(int(strdata[i*2:i*2+2], 16)))

		return ''.join(bindata)

	def stop(self):
		self.raw.stop()

class Testbed(TestbedBase):

	def __init__(self):
		self.n = 0
		self.sensor = SpectrumSensor()

		self.radios = []

	def _get_radio(self):
		for skipped in xrange(5):
			path = "/dev/ttyUSB%d" % (self.n,)
			self.n += 1

			if os.path.exists(path):
				radio = Radio(path, self.n)
				self.radios.append(radio)

				return radio

		raise TestbedError("Can't get radio device (last tried %s)" % (path,))

	def get_radio_pair(self):

		rxradio = self._get_radio()
		txradio = self._get_radio()

		rxradio.neighbor = txradio.addr
		txradio.neighbor = rxradio.addr

		return rxradio, txradio

	def start(self):
		log.debug("starting spectrum sensor")
		self.sensor.start()

		log.debug("starting radios")
		for radio in self.radios:
			radio.start()

	def stop(self):
		log.debug("stopping spectrum sensor")
		self.sensor.stop()

		log.debug("cleaning up radios")
		for radio in self.radios:
			radio.stop()

	def get_spectrum(self):
		return self.sensor.get_spectrum()

	def get_packet_size(self):
		return Radio.DATA_LEN - 1

	def time(self):
		return time.time()
