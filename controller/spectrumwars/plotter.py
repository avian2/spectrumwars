import os
import pickle
import argparse

from matplotlib import pyplot
import numpy as np

class ParsedLog:
	def __init__(self):
		self.rx = []
		self.tx = []
		self.config = []

def plot_player(log, i, out_path):
	fig = pyplot.figure(figsize=(16,10))
	ax = fig.add_subplot(121, axis_bgcolor='k')

	min_t = min(l.timestamp for l in log)
	max_t = max(l.timestamp for l in log)

	cur_ch = {}

	parsed = { 'rx': ParsedLog(), 'tx': ParsedLog() }

	payload = []
	pkt_sent = []
	pkt_recv = []

	for event in log:
		if event.data['i'] != i:
			continue

		p = parsed[event.data['role']]

		timestamp = event.timestamp - min_t

		payload.append((event.results[i].payload_bytes, timestamp))
		pkt_sent.append((event.results[i].transmit_packets, timestamp))
		pkt_recv.append((event.results[i].received_packets, timestamp))

		if event.type == "config":
			l = p.config
			ch = cur_ch[event.data['role']] = event.data['frequency']
		else:
			ch = cur_ch.get(event.data['role'], 0)
			if event.type == 'send':
				l = p.tx
			elif event.type == "recv":
				l = p.rx
			else:
				l = None

		if l is not None:
			l.append((ch, timestamp))
		elif event.type == "status":
			s = np.array(event.data['status'].spectrum)

			if 'rx' in event.data['role']:
				cmap = 'YlOrRd_r'
			else:
				cmap='YlGn_r'

			ax.scatter(range(len(s)),
					   [timestamp]*len(s),
					   c=s,
					   s=50,
					   marker='s',
					   linewidths=0,
					   cmap=cmap,
					   vmin=-70,
					   vmax=-10)

	width = 1

	def plot(l, **kwargs):
		la = np.array(l)
		if len(la.shape) == 2:
			ax.plot(la[:,0], la[:,1], ls='none', **kwargs)

	txcolor = (0,1,0)
	plot(parsed['tx'].rx, label='tx recv', color=txcolor, alpha=.5,
			marker='o', markersize=10, markeredgecolor=(.5,.1,.5), markeredgewidth=width)
	plot(parsed['tx'].tx, label='tx send', color=txcolor,
			marker='x', markeredgewidth=width)
	plot(parsed['tx'].config, label='tx config', color=txcolor,
			marker='+', markeredgewidth=width)

	rxcolor = (1,0,0)
	plot(parsed['rx'].rx, label='rx recv', color=rxcolor, alpha=.5,
			marker='o', markersize=10, markeredgecolor=(1.,.5,.5), markeredgewidth=width)
	plot(parsed['rx'].tx, label='rx send', color=rxcolor,
			marker='x', markeredgewidth=width)
	plot(parsed['rx'].config, label='rx config', color=rxcolor,
			marker='+', markeredgewidth=width)



	ax.set_ylim(0, max_t-min_t)
	ax.set_xlim(0, 64)
	pyplot.xlabel("frequency [channel]")
	pyplot.ylabel("game time [s]")

	pyplot.legend()

	pyplot.grid(color='w')


	ax = fig.add_subplot(122)
	ax.set_ylim(0, max_t-min_t)

	payload = np.array(payload)
	payloadn = np.array(payload)
	payloadn[:,0] = 100. * payload[:,0] / max(payload[:,0])

	pkt_recv = np.array(pkt_recv)
	pkt_sent = np.array(pkt_sent)

	pkt_recvn = np.array(pkt_recv)
	pkt_recvn[:,0] = 100. * pkt_recv[:,0] / max(pkt_sent[:,0])

	pkt_sentn = np.array(pkt_sent)
	pkt_sentn[:,0] = 100. * pkt_sent[:,0] / max(pkt_sent[:,0])

	def plot(l, **kwargs):
		l = np.array(l)
		ax.plot(l[:,0], l[:,1], '.-', **kwargs)

	plot(payloadn, label='payload', color='b')
	plot(pkt_recvn, label='packets recv', color='r')
	plot(pkt_sentn, label='packets sent', color='g')

	pyplot.xlabel("[%]")
	pyplot.ylabel("game time [s]")
	pyplot.legend(loc='lower right')
	pyplot.grid()

	pyplot.savefig(out_path, dpi=120, format='png')

def plot(args):
	log = pickle.load(open(args.log_path[0], "rb"))

	try:
		os.mkdir(args.out_path)
	except OSError:
		pass

	nplayers = max(l.data['i'] for l in log) + 1

	for i in xrange(nplayers):
		out_path = os.path.join(args.out_path, "player%d.png" % (i,))
		plot_player(log, i, out_path)

def main():
	parser = argparse.ArgumentParser(description="plot the progress of a spectrum wars game")

	parser.add_argument('log_path', metavar='PATH', nargs=1,
			help='path to binary log')
	parser.add_argument('-o', metavar='PATH', required=1, dest='out_path',
			help='path to write images to')

	args = parser.parse_args()

	plot(args)
