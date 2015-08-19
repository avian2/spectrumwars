from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django import forms
from django.core.exceptions import PermissionDenied

from front.models import Player, PlayerResult
import math

class PlayerForm(forms.ModelForm):
	class Meta:
		model = Player
		fields = ['name', 'code']

@login_required
def index(request):
	player_list = Player.objects.filter(user=request.user)

	for player in player_list:
		result_list = PlayerResult.objects.filter(player=player)

		packet_loss = []
		crash = []

		for result in result_list:
			crash.append(result.crashed)

			pl = result.get_packet_loss()

			if not math.isnan(pl):
				packet_loss.append(pl)

		player.crash_ratio = get_mean(crash)*100.
		player.packet_loss = get_mean(packet_loss)

	context = {
		'user': request.user,
		'player_list': sorted(player_list, key=lambda x:x.packet_loss, reverse=True),
	}

	return render(request, 'front/index.html', context)

@login_required
def player_add(request):
	if request.method == 'POST':
		form = PlayerForm(request.POST)
		if form.is_valid():

			p = Player(	user=request.user,
					name=form.cleaned_data['name'],
					code=form.cleaned_data['code'])
			p.save()

			return HttpResponseRedirect(reverse('index'))
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
def player_del(request, id):
	player = get_object_or_404(Player, pk=id)

	if player.user != request.user:
		raise PermissionDenied

	if request.method == 'POST':
		player.delete()

	return HttpResponseRedirect(reverse('index'))

@login_required
def result(request, id):
	result = get_object_or_404(PlayerResult, pk=id)

	if result.player.user != request.user:
		raise PermissionDenied

	context = {
		'result': result,
	}

	return render(request, 'front/result.html', context)

def get_mean(x):

	if len(x) > 0:
		return float(sum(x))/len(x)
	else:
		return None

def halloffame(request):

	player_list = Player.objects.all()

	for player in player_list:

		packet_loss = []
		throughput = []

		game_packet_loss = []
		other_packet_loss = []

		for result in PlayerResult.objects.filter(player=player):

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

	def do_sort(key, reverse=False):
		a = list(player_list)
		a.sort(key=lambda x:getattr(x, key), reverse=reverse)
		a.sort(key=lambda x:getattr(x, key) == None)

		return a

	most_reliable = do_sort('avg_packet_loss')
	fastest = do_sort('avg_throughput', reverse=True)
	most_cooperative = do_sort('game_packet_loss')
	best_interferer = do_sort('other_packet_loss', reverse=True)

	context = {
		'most_reliable': most_reliable,
		'fastest': fastest,
		'most_cooperative': most_cooperative,
		'best_interferer': best_interferer,
	}

	return render(request, 'front/halloffame.html', context)
