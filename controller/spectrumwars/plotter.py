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

def channel_tracker(log):
	cur_ch = {}

	for event in log:
		event.ch = cur_ch.get((event.data['i'], event.data['role']), 0)
		if event.type == "config":
			event.prevch = event.ch
			event.ch = cur_ch[(event.data['i'], event.data['role'])] = event.data['frequency']

		yield event


def plot_player(log, i, out_path):
	fig = pyplot.figure(figsize=(16,10))
	ax = fig.add_subplot(211, axis_bgcolor='k')

	min_t = min(l.timestamp for l in log)
	max_t = max(l.timestamp for l in log)

	parsed = { 'rx': ParsedLog(), 'tx': ParsedLog() }
	bg = []

	payload = []
	pkt_sent = []
	pkt_recv = []

	for event in channel_tracker(log):

		timestamp = event.timestamp - min_t

		if event.data['i'] == i:

			p = parsed[event.data['role']]


			payload.append((event.results[i].payload_bytes, timestamp))
			pkt_sent.append((event.results[i].tx_transmit_packets, timestamp))
			pkt_recv.append((event.results[i].rx_received_packets, timestamp))

			if event.type == "config":
				l = p.config
				l.append((event.prevch, timestamp))
			elif event.type == 'send':
				l = p.tx
			elif event.type == "recv":
				l = p.rx
			else:
				l = None

			if l is not None:
				l.append((event.ch, timestamp))
			elif event.type == "status":
				s = np.array(event.data['status'].spectrum)

				if 'rx' in event.data['role']:
					cmap = 'YlOrRd_r'
				else:
					cmap='YlGn_r'

				ax.scatter([timestamp]*len(s),
						range(len(s)),
						c=s,
						s=50,
						marker='s',
						linewidths=0,
						cmap=cmap,
						vmin=-70,
						vmax=-10)

		else:
			if event.type == 'send':
					bg.append((event.ch, timestamp))

	width = 1

	def plot(l, **kwargs):
		la = np.array(l)
		if len(la.shape) == 2:
			ax.plot(la[:,1], la[:,0], **kwargs)

	bgcolor = (1,1,1)
	plot(bg, color=bgcolor, alpha=.8, ls='none',
			marker='x')

	txcolor = (0,1,0)
	plot(parsed['tx'].rx, label='tx recv', color=txcolor, alpha=.5, ls='none',
			marker='o', markersize=10, markeredgecolor=(.5,.1,.5), markeredgewidth=width)
	plot(parsed['tx'].tx, label='tx send', color=txcolor, ls='none',
			marker='x', markeredgewidth=width)
	plot(parsed['tx'].config, label='tx config', color=txcolor,
			marker='+', markeredgewidth=width)

	rxcolor = (1,0,0)
	plot(parsed['rx'].rx, label='rx recv', color=rxcolor, alpha=.5, ls='none',
			marker='o', markersize=10, markeredgecolor=(1.,.5,.5), markeredgewidth=width)
	plot(parsed['rx'].tx, label='rx send', color=rxcolor, ls='none',
			marker='x', markeredgewidth=width)
	plot(parsed['rx'].config, label='rx config', color=rxcolor,
			marker='+', markeredgewidth=width)



	ax.set_xlim(0, max_t-min_t)
	# FIXME
	ax.set_ylim(0, 64)
	pyplot.xlabel("game time [s]")
	pyplot.ylabel("frequency [channel]")

	pyplot.legend()

	pyplot.grid(color='w')


	ax = fig.add_subplot(212)
	ax.set_xlim(0, max_t-min_t)

	payload = np.array(payload)
	payloadn = np.array(payload)
	payloadn[:,0] = 100. * payload[:,0] / max(payload[:,0])

	pkt_recv = np.array(pkt_recv)
	pkt_sent = np.array(pkt_sent)

	pkt_recvn = np.array(pkt_recv)
	if len(pkt_recvn):
		pkt_recvn[:,0] = 100. * pkt_recv[:,0] / max(pkt_sent[:,0])

	pkt_sentn = np.array(pkt_sent)
	if len(pkt_sentn):
		pkt_sentn[:,0] = 100. * pkt_sent[:,0] / max(pkt_sent[:,0])

	def plot(l, **kwargs):
		if len(l):
			ax.plot(l[:,1], l[:,0], '.-', **kwargs)

	plot(payloadn, label='payload', color='b')
	plot(pkt_recvn, label='packets recv', color='r')
	plot(pkt_sentn, label='packets sent', color='g')

	pyplot.xlabel("game time [s]")
	pyplot.ylabel("[%]")
	pyplot.legend(loc='lower right')
	pyplot.grid()

	pyplot.savefig(out_path, dpi=120)
	pyplot.close()

def plot_game(log, out_path):
	fig = pyplot.figure(figsize=(16,10))

	l = []

	min_t = min(l.timestamp for l in log)
	max_t = max(l.timestamp for l in log)

	bg = []

	for event in channel_tracker(log):
		if event.type == 'status' and event.data['role'] == 'log':
			l.append([event.timestamp] + list(event.data['status'].spectrum))
		elif event.type == 'send':
			bg.append((event.timestamp, event.ch))

	nl = np.array(l)

	ch_num = nl.shape[1]-1

	M = 100
	m = np.empty((ch_num, M))
	for ch in range(ch_num):
		 t = np.linspace(min_t, max_t, M)
		 m[ch,:] = np.interp(t, nl[:,0], nl[:,ch+1])

	extent = [0, max_t-min_t, 0, ch_num]

	pyplot.imshow(m, origin='lower', aspect='auto', extent=extent)
	pyplot.colorbar()
	pyplot.grid()

	nbg = np.array(bg)
	nbg[:,0] -= min_t

	pyplot.plot(nbg[:,0], nbg[:,1], color='w', ls='none', marker='x', markeredgewidth=2)
	pyplot.axis(extent)

	pyplot.xlabel("game time [s]")
	pyplot.ylabel("frequency [channel]")

	pyplot.savefig(out_path, dpi=120)
	pyplot.close()


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

	out_path = os.path.join(args.out_path, "game.png")
	plot_game(log, out_path)

def main():
	parser = argparse.ArgumentParser(description="plot the progress of a spectrum wars game")

	parser.add_argument('log_path', metavar='PATH', nargs=1,
			help='path to binary log')
	parser.add_argument('-o', metavar='PATH', required=1, dest='out_path',
			help='path to write images to')

	args = parser.parse_args()

	plot(args)
