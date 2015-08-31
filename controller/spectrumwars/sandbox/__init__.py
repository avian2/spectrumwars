import time

class SandboxError(Exception): pass

class SandboxPlayer(object):
	def __init__(self, rx, tx, i):
		self.rx = rx
		self.tx = tx
		self.i = i

class SandboxBase(object):
	def get_players(self):
		raise NotImplementedError

	def stop(self):
		pass

class SandboxTransceiverBase(object):
	def init(self, i, update_interval):
		raise NotImplementedError

	def start(self, endpoint):
		raise NotImplementedError

	def join(self, deadline=None, timefunc=time.time):
		raise NotImplementedError
