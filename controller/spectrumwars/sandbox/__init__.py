import time

class SandboxError(Exception): pass

class SandboxPlayer(object):
	def __init__(self, dst, src, i):
		self.dst = dst
		self.src = src
		self.i = i

class SandboxBase(object):
	def get_players(self):
		raise NotImplementedError

	def get_iface(self):
		pass

	def start(self):
		pass

	def stop(self):
		pass

class SandboxTransceiverBase(object):
	def __init__(self, i, role):
		self.i = i
		self.role = role

	def init(self, update_interval):
		raise NotImplementedError

	def start(self, endpoint):
		raise NotImplementedError

	def join(self, deadline=None, timefunc=time.time):
		raise NotImplementedError
