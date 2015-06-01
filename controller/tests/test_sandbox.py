import unittest
from tempfile import NamedTemporaryFile

from spectrumwars.sandbox import Sandbox

class TestSandbox(unittest.TestCase):

	def test_empty(self):
		sandbox = Sandbox([])

		players = sandbox.get_players()

		self.assertEqual(players, [])


	def test_simple(self):
		f = NamedTemporaryFile(suffix='.py')
		f.write("""from spectrumwars import Transceiver

class Receiver(Transceiver):
	pass

class Transmitter(Transceiver):
	pass
""")
		f.flush()

		sandbox = Sandbox([f.name])

		players = sandbox.get_players()

		self.assertEqual(len(players), 1)
