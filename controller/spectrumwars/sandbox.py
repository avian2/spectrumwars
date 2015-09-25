import imp
import json
import logging
import os
import subprocess
import sys
import re
import threading
import time
import traceback
from spectrumwars.rpc import RPCClient

from spectrumwars import Player

log = logging.getLogger(__name__)

class SandboxError(Exception): pass

class SandboxPlayer(object):
	def __init__(self, dst, src, i):
		self.dst = dst
		self.src = src
		self.i = i

# ThreadedSandbox provides no isolation between the player's code and the game
# controller. It is mostly used for debugging and as an example of how the
# Sandbox interface works.

class ThreadedSandboxInstance(object):
	def __init__(self, cls, role):
		self.cls = cls
		self.role = role

	def init(self, i, update_interval):
		self.ins = self.cls(i, self.role, update_interval)

	def start(self, endpoint):
		client = RPCClient(endpoint)

		self.thread = threading.Thread(target=self.ins._start, args=(client,))
		self.thread.start()

	def join(self, deadline=None, timefunc=time.time):
		self.thread.join()

class ThreadedSandbox(object):
	def __init__(self, cls_list):
		self.players = []

		for i, (dst_cls, src_cls) in enumerate(cls_list):
			player = SandboxPlayer(
				ThreadedSandboxInstance(dst_cls, 'dst'),
				ThreadedSandboxInstance(src_cls, 'src'), i)
			self.players.append(player)

	def get_players(self):
		return self.players

class SubprocessSandboxInstance(object):
	def __init__(self, path, role):
		self.path = path
		self.role = role

	def init(self, i, update_interval):
		self.i = i
		self.update_interval = update_interval

	def start(self, endpoint):

		self.endpoint = endpoint

		cmdname = 'spectrumwars_sandbox'

		for dirname in os.environ['PATH'].split(':'):
			excpath = os.path.join(dirname, cmdname)
			if os.path.exists(excpath):
				break
		else:
			raise SandboxError("Can't find %r in PATH" % (cmdname,))

		args_json = json.dumps({
			'path': self.path,
			'i': self.i,
			'role': self.role,
			'update_interval': self.update_interval,
			'endpoint': endpoint,
			'loglevel': logging.getLogger().getEffectiveLevel() })
		cmd = (excpath, args_json)

		self.p = subprocess.Popen(cmd)

	def join(self, deadline=None, timefunc=time.time):
		if deadline is None:
			rc = self.p.wait()
		else:
			interval = .5
			while True:
				rc = self.p.poll()
				if rc != None:
					break

				if timefunc() >= deadline:
					log.warning("(%d %s) sandbox killing instance due to deadline" %
							(self.i, self.role))
					self.p.kill()

				time.sleep(interval)
			else:
				return True
		if rc != 0:
			client = RPCClient(self.endpoint)
			if rc == -9:
				desc = "Time limit reached"
			else:
				desc = "Sandbox exited with return code %d" % (rc,)
			client.report_stop(True, desc)

		# If sandbox instance exited normally, it should have reported
		# the stop itself.

		return False

	@classmethod
	def run(cls):
		args_json = sys.argv[1]
		args = json.loads(args_json)

		logging.basicConfig(level=args['loglevel'],
				format="<SB>%(levelname)s:%(name)s:%(message)s")
		logging.getLogger('jsonrpc2_zeromq').setLevel(logging.WARNING)

		log.info("(%d %s) sandbox starting" % (args['i'], args['role']))

		client = RPCClient(args['endpoint'])

		name = os.path.basename(args['path'])
		name = re.sub("\.py$", "", name)

		try:
			mod = imp.load_source(name, args['path'])
		except:
			log.warning("(%d %s) exception on import" % (args['i'], args['role']))
			desc = traceback.format_exc()
			client.report_stop(True, desc)
		else:
			if args['role'] == 'dst':
				try:
					cls = mod.Destination
				except AttributeError:
					cls = mod.Receiver
			else:
				try:
					cls = mod.Source
				except AttributeError:
					cls = mod.Transmitter

			ins = cls(args['i'], args['role'], args['update_interval'])
			ins._start(client)

		log.info("(%d %s) sandbox stopping" % (args['i'], args['role']))

class SubprocessSandbox(object):
	def __init__(self, paths):
		self.paths = paths

	def get_players(self):
		players = []

		for i, path in enumerate(self.paths):
			dst = SubprocessSandboxInstance(path, 'dst')
			src = SubprocessSandboxInstance(path, 'src')

			player = SandboxPlayer(dst, src, i)
			players.append(player)

		log.info("Loaded %d players" % (len(players),))

		return players
