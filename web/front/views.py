from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django import forms
from django.core.exceptions import PermissionDenied
from django.db import transaction

from front.models import Player, PlayerResult, Round, Game
import math

class PlayerForm(forms.ModelForm):
	class Meta:
		model = Player
		fields = ['name', 'code']

@login_required
def user(request):
	player_list = Player.objects.filter(user=request.user)

	for player in player_list:
		result_list = PlayerResult.objects.filter(player=player)

		packet_loss = []
		crash = []

		for result in result_list:
			crash.append(int(result.crashed)*100)

			pl = result.get_packet_loss()

			if not math.isnan(pl):
				packet_loss.append(pl)

		player.crash_ratio = get_mean(crash)
		player.packet_loss = get_mean(packet_loss)

	player_list_sorted = sorted(player_list, key=lambda x:(x.crash_ratio, x.packet_loss))

	context = {
		'user': request.user,
		'player_list': player_list_sorted,
	}

	return render(request, 'front/user.html', context)

@login_required
def player_add(request):
	if request.method == 'POST':
		form = PlayerForm(request.POST)
		if form.is_valid():

			p = Player(	user=request.user,
					name=form.cleaned_data['name'],
					code=form.cleaned_data['code'],
					enabled=True,
					in_use=False)
			p.save()

			return HttpResponseRedirect(reverse('user'))
	else:
		form = PlayerForm()

	context = { 'form': form }

	return render(request, 'front/player_add.html', context)

@login_required
def player(request, id):
	player = get_object_or_404(Player, pk=id)

	if player.user != request.user:
		raise PermissionDenied

	result_list = PlayerResult.objects.filter(player=player)

	context = {
		'player': player,
		'result_list': result_list,
		'user': request.user,
	}

	return render(request, 'front/player.html', context)

@login_required
def player_enable(request, id):
	player = get_object_or_404(Player, pk=id)

	if player.user != request.user:
		raise PermissionDenied

	if request.method == 'POST':
		player.enabled = True
		player.save()

	return HttpResponseRedirect(reverse('player', args=(id,)))

@login_required
def player_disable(request, id):
	player = get_object_or_404(Player, pk=id)

	if player.user != request.user:
		raise PermissionDenied

	if request.method == 'POST':
		player.enabled = False
		player.save()

	return HttpResponseRedirect(reverse('player', args=(id,)))

@login_required
def player_delete(request, id):
	player = get_object_or_404(Player, pk=id)

	if player.user != request.user:
		raise PermissionDenied

	with transaction.atomic():
		if player.in_use:
			raise PermissionDenied

		if request.method == 'POST':
			player.delete()

	return HttpResponseRedirect(reverse('user'))

@login_required
def result(request, id):
	result = get_object_or_404(PlayerResult, pk=id)

	if result.player.user != request.user:
		raise PermissionDenied

	context = {
		'result': result,
	}

	return render(request, 'front/result.html', context)

def rounds(request):

	round_list = []

	for round in Round.objects.all():

		game_list = Game.objects.filter(round=round)

		round.n_games = game_list.count()

		players = set()
		for result in PlayerResult.objects.filter(game__in=game_list):
			players.add(result.player.id)

		round.n_players = len(players)

		round_list.append(round)

	user_set = set()
	player_num = 0
	for player in Player.objects.filter(enabled=True):
		user_set.add(player.user.id)
		player_num += 1

	context = {
		'round_list': round_list,
		'player_num': player_num,
		'user_num': len(user_set),
	}

	return render(request, 'front/rounds.html', context)

def get_mean(x):

	if len(x) > 0:
		return float(sum(x))/len(x)
	else:
		return None

def round(request, id):
	round = get_object_or_404(Round, pk=id)
	game_list = Game.objects.filter(round=round)

	player_list = Player.objects.all()

	player_list2 = []
	for player in player_list:

		packet_loss = []
		throughput = []

		game_packet_loss = []
		other_packet_loss = []

		in_round = False

		for result in PlayerResult.objects.filter(player=player, game__in=game_list):

			in_round = True

			had_crash = False
			for result2 in PlayerResult.objects.filter(game=result.game):
				if result2.crashed:
					had_crash = True
					break
			if had_crash:
				continue

			for result2 in PlayerResult.objects.filter(game=result.game):

				game_packet_loss.append(result2.get_packet_loss())

				if result2.id != result.id:
					other_packet_loss.append(result2.get_packet_loss())

			packet_loss.append(result.get_packet_loss())
			throughput.append(result.get_throughput())

		player.avg_packet_loss = get_mean(packet_loss)
		player.avg_throughput = get_mean(throughput)
		player.game_packet_loss = get_mean(game_packet_loss)
		player.other_packet_loss = get_mean(other_packet_loss)

		if in_round:
			player_list2.append(player)

	def do_sort(key, reverse=False):
		a = list(player_list2)
		a.sort(key=lambda x:getattr(x, key), reverse=reverse)
		a.sort(key=lambda x:getattr(x, key) == None)

		return a

	most_reliable = do_sort('avg_packet_loss')
	fastest = do_sort('avg_throughput', reverse=True)
	most_cooperative = do_sort('game_packet_loss')
	best_interferer = do_sort('other_packet_loss', reverse=True)

	context = {
		'round': round,
		'game_list': game_list,
		'most_reliable': most_reliable,
		'fastest': fastest,
		'most_cooperative': most_cooperative,
		'best_interferer': best_interferer,
	}

	return render(request, 'front/round.html', context)
