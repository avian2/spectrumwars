from django.core.management.base import BaseCommand, CommandError
from django.core.files import File

from front import models

import itertools
import logging

from spectrumwars.testbed.simulation import Testbed
from spectrumwars.sandbox import SubprocessSandbox
from spectrumwars import Game, GameController
from spectrumwars.plotter import plot_player

import tempfile
import StringIO

log = logging.getLogger(__name__)

def run_game(code_list):
	logging.basicConfig(level=logging.DEBUG)
	logging.getLogger('jsonrpc2_zeromq').setLevel(logging.WARNING)

	file_list = []

	for code in code_list:
		f = tempfile.NamedTemporaryFile(suffix='.py', delete=True)
		f.write(code)
		f.flush()

		file_list.append(f)

	testbed = Testbed()
	sandbox = SubprocessSandbox([f.name for f in file_list])

	game = Game(testbed, sandbox, packet_limit=50, time_limit=30)
	ctl = GameController()

	log.info("Running game...")

	result_list = ctl.run(game)

	log.info("Done.")

	for f in file_list:
		f.close()

	return game, result_list

def record_game(player_list):

	gameo, result_list = run_game([player.code for player in player_list])

	duration = gameo.end_time - gameo.start_time

	game = models.Game(duration=duration)
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

class Command(BaseCommand):
	help = 'Runs some games'

	def handle(self, *args, **options):
		all_player_list = models.Player.objects.all()
		for player_list in itertools.combinations(all_player_list, 2):
			record_game(player_list)
