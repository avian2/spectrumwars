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

import logging
import os
import pyudev
import serial
import threading
import time
import Queue

from spectrumwars.testbed import TestbedBase, RadioBase, RadioTimeout, RadioError, TestbedError, RadioPacket
from spectrumwars.testbed.usrp_sensing import SpectrumSensor

log = logging.getLogger(__name__)

def list_radio_devices():
	context = pyudev.Context()

	l = []
	for device in context.list_devices(subsystem='tty', ID_MODEL='VESNA_SpectrumWars_radio'):
		l.append(device['DEVNAME'])

	return l

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

	PACKET_SIZE = 252
	CMD_RETRIES = 3

	def __init__(self, path, addr):
		super(Radio, self).__init__()

		self.raw = RadioRaw(path)
		self.addr = addr
		self.config = (0, 0, 0)

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

	def binsend(self, bindata):

		assert len(bindata) <= self.PACKET_SIZE
		strdata = ''.join(("%02x" % ord(v)) for v in bindata)

		self._cmd("t %02x %s" % (self.neighbor, strdata))

	def set_configuration(self, frequency, bandwidth, power):
		config = (frequency, bandwidth, power)
		self._cmd("c %x %x %x" % config)
		self.config = config

	def get_configuration(self):
		return self.config

	def binrecv(self, timeout=1.):
		data = self.raw.recv(timeout=timeout)

		assert data.startswith("R ")

		strdata = data[2:]

		assert len(strdata) % 2 == 0
		n = len(strdata) / 2

		assert n <= self.PACKET_SIZE

		bindata = []
		for i in xrange(n):
			bindata.append(chr(int(strdata[i*2:i*2+2], 16)))

		return ''.join(bindata)

	def stop(self):
		self.raw.stop()

class Testbed(TestbedBase):

	RADIO_CLASS = Radio

	def __init__(self):
		self.n = 0
		self.sensor = SpectrumSensor(base_hz=2.4e9, step_hz=100e3, nchannels=64)

		self.radio_devices = list_radio_devices()
		log.debug("detected %d connected radios" % (len(self.radio_devices,)))

		self.radios = []

	def _get_radio(self):

		try:
			path = self.radio_devices.pop()
		except IndexError:
			raise TestbedError("Can't get radio device")

		self.n += 1

		radio = Radio(path, self.n)
		self.radios.append(radio)

		return radio

	def get_radio_pair(self):

		dst_radio = self._get_radio()
		src_radio = self._get_radio()

		dst_radio.neighbor = src_radio.addr
		src_radio.neighbor = dst_radio.addr

		return dst_radio, src_radio

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

	def get_frequency_range(self):
		return min(self.sensor.fft_size, 256)

	def get_bandwidth_range(self):
		return 4

	def get_power_range(self):
		return 17
