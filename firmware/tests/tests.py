import serial
import unittest
import threading
import Queue

class RadioError(Exception): pass
class RadioTimeout(Exception): pass

class Radio(object):

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
			raise RadioTimeout("timeout waiting for response to %r" % (cmd,))
		elif resp == "O":
			pass
		elif resp.startswith("E "):
			raise RadioError(resp[2:])
		else:
			print resp
			assert False

	def recv(self):
		try:
			resp = self.rx_queue.get(timeout=self.RECEIVE_TIMEOUT)
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
		print "%s >>> %s" % (self.device, msg)

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

class OnLineRadioTestCase(unittest.TestCase):

	NODE_1_DEV = "/dev/ttyUSB0"
	NODE_2_DEV = "/dev/ttyUSB1"

	@classmethod
	def setUpClass(self):
		self.node1 = Radio(self.NODE_1_DEV)
		self.node2 = Radio(self.NODE_2_DEV)

	@classmethod
	def tearDownClass(self):
		self.node1.stop()
		self.node2.stop()

class TestRadioInterface(OnLineRadioTestCase):

	def test_set_address(self):
		self.node2.cmd("a 01")

	def test_invalid_cmd(self):
		self.assertRaisesRegexp(RadioError, "unknown command", self.node1.cmd, "x")

	def test_send_invalid_1(self):
		self.assertRaises(RadioError, self.node1.cmd, "t 02 0123456789abcde")

	def test_send_invalid_2(self):
		self.assertRaises(RadioError, self.node1.cmd, "t 02 0x23456789abcde")

	def test_send_invalid_3(self):
		self.assertRaises(RadioError, self.node1.cmd, "t 02 " + "01" * 254)

class TestRadio(OnLineRadioTestCase):
	def setUp(self):
		for node in self.node1, self.node2:
			node.cmd("a 00")
			node.cmd("c 0 0 0")

	def test_set_address_1(self):
		self.node2.cmd("a 01")
		self._send_one(addr=1)
		self.node2.cmd("a 00")

	def test_set_address_1(self):
		self.node2.cmd("a 01")
		self.assertRaises(RadioTimeout, self._send_one, addr=2)
		self.node2.cmd("a 00")

	def _send_one(self, addr=0, n=20):
		data = "cd" * n
		self.node1.cmd("t %x %s" % (addr, data))
		expected = "R %s" % (data,)

		resp = self.node2.recv()
		self.assertEqual(resp, expected)

	def test_length(self):
		for bw in xrange(4):
			self.node1.cmd("c 0 %x 0" % (bw,))
			self.node2.cmd("c 0 %x 0" % (bw,))
			for n in xrange(1, 253, 10):
				print bw, n
				self._send_one(n=n)

	def test_short(self):
		for bw in xrange(4):
			self.node1.cmd("c 0 %x 0" % (bw,))
			self.node2.cmd("c 0 %x 0" % (bw,))
			self._send_one(n=1)

	def test_send_min_len(self):
		self._send_one(n=1)

	def test_send_max_len(self):
		self._send_one(n=252)

	def off_test_send_many(self):
		for n in xrange(1000):
			self._send_one()

	def test_send_collision(self):
		self.node1.cmd("a 01")
		self.node2.cmd("a 02")
		for n in xrange(50):
			self.node1.cmd("t 02 " + "ab" * 10)
			self.node2.cmd("t 01 " + "ab" * 10)
		self.node1.cmd("a 00")
		self.node2.cmd("a 00")

		self.node1.recv_flush()
		self.node2.recv_flush()

	def test_long_null_packet(self):
		# this fails if data whitening isn't working
		data = "00" * 252
		N = 10

		for n in xrange(N):
			self.node1.cmd("t 0 %s" % (data,))

		expected = "R %s" % (data,)
		for n in xrange(N):
			resp = self.node2.recv()
			self.assertEqual(resp, expected)

	def test_config_1(self):
		for chan in xrange(0, 255, 50):
			for bw in xrange(4):
				self.node1.cmd("c %x %x 0" % (chan, bw))
				self.node2.cmd("c %x %x 0" % (chan, bw))
				self._send_one()

	def test_config_2(self):
		self.node1.cmd("c 1 0 0")
		self.assertRaises(RadioTimeout, self._send_one)

	def test_config_3(self):
		self.node1.cmd("c 0 1 0")
		self.assertRaises(RadioTimeout, self._send_one)

if __name__ == "__main__":
	unittest.main()
