import pickle
import argparse

from matplotlib import pyplot
import numpy as np

def plot(args):
	log = pickle.load(open(args.log_path[0], "rb"))

	fig = pyplot.figure(figsize=(8,10))
	ax = fig.add_subplot(111, axis_bgcolor='k')

	min_t = min(l.timestamp for l in log)
	max_t = max(l.timestamp for l in log)

	cur_ch = {}

	for event in log:
		
		def pl(ch, marker):
			if 'rx' == event.data['role']:
				color = (1,0,0)
			else:
				color = (0,1,0)
			
			if marker=='o':
				alpha = .5
				size=10
				edge=tuple(((np.array(color)+1)/2.))
			else:
				alpha = 1.
				size=7
				edge=color
		
			ax.plot([ch], [event.timestamp-min_t], alpha=alpha, marker=marker, color=color, markersize=size, markeredgecolor=edge, markeredgewidth=1)
		
		if event.type == "config":
			pl(marker='+', ch=event.data['frequency'])
			cur_ch[event.data['role']] = event.data['frequency']
		elif event.type == "send":
			pl(marker='x', ch=cur_ch.get(event.data['role'], 0))
		elif event.type == "recv":
			pl(marker='o', ch=cur_ch.get(event.data['role'], 0))
		elif event.type == "status":
			s = np.array(event.data['status'].spectrum)
			#s -= min(s)
			#if max(s) > min(s):
			#	s /= (max(s)-min(s))
			
			if 'rx' in event.data['role']:
				cmap = 'YlOrRd_r'
			else:
				cmap='YlGn_r'
				
			ax.scatter(range(len(s)), 
					   [event.timestamp - min_t]*len(s), 
					   c=s, 
					   s=50, 
					   marker='s', 
					   linewidths=0,
					   cmap=cmap,
					   vmin=-70,
					   vmax=-10)
			
	ax.set_ylim(0, max_t-min_t)
	ax.set_xlim(0, 64)
	pyplot.xlabel("channel")
	pyplot.ylabel("time [s]")

	pyplot.grid(color='w')

	pyplot.savefig(args.out_path, dpi=120)

def main():
	parser = argparse.ArgumentParser(description="plot the progress of a spectrum wars game")

	parser.add_argument('log_path', metavar='PATH', nargs=1,
			help='path to binary log')
	parser.add_argument('-o', metavar='PATH', required=1, dest='out_path',
			help='path to write images to')

	args = parser.parse_args()

	plot(args)
