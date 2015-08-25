import datetime

from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.db import transaction
from django.utils import timezone

from front import models

import itertools
import logging
import signal

from spectrumwars.runner import get_testbed
from spectrumwars.sandbox import SubprocessSandbox
from spectrumwars import Game, GameController
from spectrumwars.plotter import plot_player, plot_game

import tempfile
import time
import StringIO

log = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('jsonrpc2_zeromq').setLevel(logging.WARNING)

want_stop = False

def run_game(code_list, testbed):
	file_list = []

	for code in code_list:
		f = tempfile.NamedTemporaryFile(suffix='.py', delete=True)
		f.write(code)
		f.flush()

		file_list.append(f)

	sandbox = SubprocessSandbox([f.name for f in file_list])

	game = Game(testbed, sandbox, packet_limit=None, time_limit=30)
	ctl = GameController()

	log.info("Running game...")

	result_list = ctl.run(game)

	log.info("Done.")

	for f in file_list:
		f.close()

	return game, result_list

def record_game(round, player_list, testbed):

	gameo, result_list = run_game([player.code for player in player_list], testbed)

	duration = gameo.end_time - gameo.start_time

	game = models.Game(round=round, duration=duration)
	game.save()

	for i, result in enumerate(result_list):

		player = player_list[i]

		if result.crashed:
			crash_log = '\n'.join(result.crash_report)
		else:
			crash_log = ''

		robj = models.PlayerResult(
			game=game,
			player=player,

			transmit_packets=result.transmit_packets,
			received_packets=result.received_packets,
			payload_bytes=result.payload_bytes,

			crashed=result.crashed,
			log=crash_log,
			timeline=None
		)
		robj.save()

		if gameo.log:
			timeline_img = StringIO.StringIO()
			plot_player(gameo.log, i, timeline_img)

			robj.timeline.save("timeline_%d.png" % (robj.id,), File(timeline_img))

	if gameo.log:
		timeline_img = StringIO.StringIO()
		plot_game(gameo.log, timeline_img)

		game.timeline.save("game_timeline_%d.png" % (game.id,), File(timeline_img))


def handler(signum, frame):
	global want_stop
	print "Signal %d caught! Stopping..." % (signum,)
	want_stop = True


class Command(BaseCommand):
	help = 'Runs some games'

	def add_arguments(self, parser):
		parser.add_argument('-n', metavar="N", dest='nplayers', type=int, default=1,
				help="Number of players per game")
		parser.add_argument('-t', '--testbed', metavar='TESTBED', dest='testbed',
				default='simulation', help='testbed to use (default: simulation)')
		parser.add_argument('-O', '--testbed-option', metavar='KEY=VALUE', nargs='*',
				dest='testbed_options', help='testbed options')
		parser.add_argument('-p', '--period', metavar='MINUTES', dest='period', type=int, default=0,
				help="run a round once per MINUTES")

	def handle(self, *args, **options):

		signal.signal(signal.SIGTERM, handler)
		signal.signal(signal.SIGINT, handler)

		period = datetime.timedelta(seconds=options['period']*60)

		start_time = timezone.now()

		while not want_stop:

			if options['period'] > 0:
				self.clean_stale(period)

			start_time += period

			round = models.Round(
					nplayers=options['nplayers'],
					testbed=options['testbed'],
					state='scheduled',
					start_time=start_time)
			round.save()


			log.info("Waiting until %s" % (round.start_time,))
			while (not want_stop) and (timezone.now() < round.start_time):
				time.sleep(2)

			if want_stop:
				break


			round.state = 'started'
			round.save()


			# Atomically mark all currently existing players as in-use. This makes
			# them impossible to delete.
			with transaction.atomic():
				all_player_list = models.Player.objects.filter(enabled=True)
				for player in all_player_list:
					player.in_use = True
					player.save()

			for player_list in itertools.combinations(all_player_list, options['nplayers']):
				testbed = get_testbed(options['testbed'], options['testbed_options'])
				record_game(round, player_list, testbed)

			round.finish_time = timezone.now()
			round.state = 'finished'
			round.save()


			if options['period'] == 0:
				break

	def clean_stale(self, period):

		now = timezone.now()

		for round in models.Round.objects.filter(state__in=('started', 'scheduled')):
			d = now - round.start_time

			if d > period*2:
				log.info("Cleaning stale round %s" % (round,))
				round.delete()
