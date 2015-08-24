from django.core.management.base import BaseCommand, CommandError
from django.core.files import File

from front import models

import itertools
import logging

from spectrumwars.runner import get_testbed
from spectrumwars.sandbox import SubprocessSandbox
from spectrumwars import Game, GameController
from spectrumwars.plotter import plot_player, plot_game

import tempfile
import StringIO

log = logging.getLogger(__name__)

def run_game(code_list, testbed):
	logging.basicConfig(level=logging.DEBUG)
	logging.getLogger('jsonrpc2_zeromq').setLevel(logging.WARNING)

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


class Command(BaseCommand):
	help = 'Runs some games'

	def add_arguments(self, parser):
		parser.add_argument('-n', metavar="N", dest='nplayers', type=int, default=1,
				help="Number of players per game")
		parser.add_argument('-t', '--testbed', metavar='TESTBED', dest='testbed',
				default='simulation', help='testbed to use (default: simulation)')
		parser.add_argument('-O', '--testbed-option', metavar='KEY=VALUE', nargs='*',
				dest='testbed_options', help='testbed options')

	def handle(self, *args, **options):

		testbed = get_testbed(options['testbed'], options['testbed_options'])

		round = models.Round(
				nplayers=options['nplayers'],
				testbed=options['testbed'],
				state='started')
		round.save()

		all_player_list = models.Player.objects.filter(enabled=True)
		for player_list in itertools.combinations(all_player_list, options['nplayers']):
			record_game(round, player_list, testbed)

		round.state = 'finished'
		round.save()
