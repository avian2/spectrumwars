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

import jsonrpc2_zeromq
import time
import zmq

RPCClient = jsonrpc2_zeromq.RPCClient

class RPCServer(jsonrpc2_zeromq.RPCServer):

	RETRY_PORT = 10

	def __init__(self, *args, **kwargs):
		# This is a bit of a hack, but for some unknown reason it
		# sometimes throws "Address already in use" even though
		# previous RPCServer instance has been destroyed.
		for i in xrange(self.RETRY_PORT):
			try:
				super(RPCServer, self).__init__(*args, **kwargs)
			except zmq.ZMQError, e:
				time.sleep(.1)
			else:
				break
		else:
			raise e
