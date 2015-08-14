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
