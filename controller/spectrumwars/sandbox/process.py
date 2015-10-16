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
from spectrumwars.sandbox import SandboxPlayer, SandboxError, SandboxBase, SandboxTransceiverBase

log = logging.getLogger(__name__)

class SubprocessSandboxTransceiver(SandboxTransceiverBase):
	def __init__(self, path, i, role):
		super(SubprocessSandboxTransceiver, self).__init__(i, role)
		self.path = path

	def init(self, update_interval):
		self.update_interval = update_interval

	def get_args_json(self, path):

		args_json = json.dumps({
			'path': path,
			'i': self.i,
			'role': self.role,
			'update_interval': self.update_interval,
			'endpoint': self.endpoint,
			'loglevel': logging.getLogger().getEffectiveLevel()
		})

		return args_json

	def start(self, endpoint):

		self.endpoint = endpoint

		cmdname = 'spectrumwars_sandbox'

		for dirname in os.environ['PATH'].split(':'):
			excpath = os.path.join(dirname, cmdname)
			if os.path.exists(excpath):
				break
		else:
			raise SandboxError("Can't find %r in PATH" % (cmdname,))

		args_json = self.get_args_json(self.path)
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

class SubprocessSandbox(SandboxBase):
	def __init__(self, paths):
		self.paths = paths

	def get_players(self):
		players = []

		for i, path in enumerate(self.paths):
			dst = SubprocessSandboxTransceiver(path, i, 'dst')
			src = SubprocessSandboxTransceiver(path, i, 'src')

			player = SandboxPlayer(dst, src, i)
			players.append(player)

		log.info("Loaded %d players" % (len(players),))

		return players
