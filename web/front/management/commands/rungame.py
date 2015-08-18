from django.core.management.base import BaseCommand, CommandError

from front import models

import logging

from spectrumwars.testbed.simulation import Testbed
from spectrumwars.sandbox import SubprocessSandbox
from spectrumwars import Game, GameController

import tempfile

log = logging.getLogger(__name__)

def run_game(code):
	logging.basicConfig(level=logging.DEBUG)
	logging.getLogger('jsonrpc2_zeromq').setLevel(logging.WARNING)

	f = tempfile.NamedTemporaryFile(suffix='.py', delete=True)
	f.write(code)
	f.flush()

	testbed = Testbed()
	sandbox = SubprocessSandbox([f.name])

	game = Game(testbed, sandbox, packet_limit=50, time_limit=30)
	ctl = GameController()

	log.info("Running game...")

	results = ctl.run(game)

	log.info("Done.")

	game_time = game.end_time - game.start_time
	print "Game time: %.1f seconds" % (game_time,)

	f.close()

	return results[0]

class Command(BaseCommand):
	help = 'Runs some games'

	def handle(self, *args, **options):
		player_list = models.Player.objects.all()
		player = player_list[0]

		result = run_game(player.code)

		game = models.Game()
		game.save()

		robj = models.PlayerResult(
			game=game,
			player=player,
			received_ratio=0,
			crashed=result.crashed,
			log=result.crash_desc if result.crashed else '',
			timeline=None
		)
		robj.save()
