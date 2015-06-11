import imp
import json
import logging
import os
import subprocess
import sys
import re
import threading
import time
from jsonrpc2_zeromq import RPCClient

from spectrumwars import Player

log = logging.getLogger(__name__)

class SandboxPlayer(object):
	def __init__(self, rx, tx, i):
		self.rx = rx
		self.tx = tx
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

	def join(self, deadline=None):
		self.thread.join()

class ThreadedSandbox(object):
	def __init__(self, cls_list):
		self.players = []

		for i, (rxcls, txcls) in enumerate(cls_list):
			player = SandboxPlayer(
				ThreadedSandboxInstance(rxcls, 'rx'),
				ThreadedSandboxInstance(txcls, 'tx'), i)
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
			'endpoint': endpoint})
		cmd = (excpath, args_json)

		self.p = subprocess.Popen(cmd)

	def join(self, deadline=None):
		if deadline is None:
			rc = self.p.wait()
		else:
			interval = .5
			while True:
				if time.time() >= deadline:
					self.p.kill()
					time.sleep(interval)

				rc = self.p.poll()
				if rc != None:
					break
				time.sleep(interval)
			else:
				return True
		if rc != 0:
			client = RPCClient(self.endpoint)
			client.report_stop(True)

		return False

	@classmethod
	def run(cls):
		logging.basicConfig(level=logging.DEBUG)
		logging.getLogger('jsonrpc2_zeromq').setLevel(logging.WARNING)

		args_json = sys.argv[1]
		args = json.loads(args_json)

		client = RPCClient(args['endpoint'])

		name = os.path.basename(args['path'])
		name = re.sub("\.py$", "", name)

		mod = imp.load_source(name, args['path'])

		if args['role'] == 'rx':
			cls = mod.Receiver
		else:
			cls = mod.Transmitter

		ins = cls(args['i'], args['role'], args['update_interval'])
		ins._start(client)

class SubprocessSandbox(object):
	def __init__(self, paths):
		self.paths = paths

	def get_players(self):
		players = []

		for i, path in enumerate(self.paths):
			sbrx = SubprocessSandboxInstance(path, 'rx')
			sbtx = SubprocessSandboxInstance(path, 'tx')

			player = SandboxPlayer(sbrx, sbtx, i)
			players.append(player)

		log.info("Loaded %d players" % (len(players),))

		return players
