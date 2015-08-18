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
		for player in player_list:
			result = run_game(player.code)

			game = models.Game()
			game.save()

			if result.crashed:
				crash_log = ''.join(result.crash_desc)
			else:
				crash_log = ''

			if result.transmit_packets > 0:
				ratio = 100. * result.received_packets / result.transmit_packets
			else:
				ratio = 0.


			robj = models.PlayerResult(
				game=game,
				player=player,
				received_ratio=ratio,
				crashed=result.crashed,
				log=crash_log,
				timeline=None
			)
			robj.save()
