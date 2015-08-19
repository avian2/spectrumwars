from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django import forms
from django.core.exceptions import PermissionDenied

from front.models import Player, PlayerResult

class PlayerForm(forms.ModelForm):
	class Meta:
		model = Player
		fields = ['name', 'code']

@login_required
def index(request):
	player_list = Player.objects.filter(user=request.user)

	for player in player_list:
		result_list = PlayerResult.objects.filter(player=player)

		alln = 0
		crashn = 0

		avgratio = 0.
		for result in result_list:
			if result.crashed:
				crashn += 1
			alln += 1

			avgratio += result.received_ratio

		if alln > 0:
			avgratio /= alln
			crashratio = float(crashn)/alln
		else:
			avgratio = float("NaN")
			crashratio = float("NaN")

		player.crash_ratio = crashratio
		player.packet_ratio = avgratio

	context = {
		'user': request.user,
		'player_list': player_list,
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

def halloffame(request):

	player_list = Player.objects.all()

	for player in player_list:

		n = 0
		avg_ratio = 0.
		avg_throughput = 0.

		n2 = 0
		avg_ratio_combined = 0.
		max_ratio_others = 0.

		for result in PlayerResult.objects.filter(player=player):
			ratio = result.received_ratio
			throughput = result.payload_bytes / result.game.duration

			avg_ratio += ratio
			avg_throughput += throughput

			n += 1

			for result2 in PlayerResult.objects.filter(game=result.game):
				avg_ratio_combined += result2.received_ratio
				n2 += 1

				if result2.id != result.id:
					max_ratio_others = max(max_ratio_others, result2.received_ratio)

		if n > 0:
			player.avg_ratio = avg_ratio / n
			player.avg_throughput = avg_throughput / n
		else:
			player.avg_ratio = float("NaN")
			player.avg_throughput = float("NaN")

		if n2 > 0:
			player.avg_ratio_combined = avg_ratio / n2
		else:
			player.avg_ratio_combined = float("NaN")

		player.max_ratio_others = max_ratio_others

	limit = 10

	most_reliable = sorted(player_list, key=lambda x:x.avg_ratio, reverse=True)[:limit]
	fastest = sorted(player_list, key=lambda x:x.avg_throughput, reverse=True)[:limit]
	most_cooperative = sorted(player_list, key=lambda x:x.avg_ratio_combined, reverse=True)[:limit]
	best_interferer = sorted(player_list, key=lambda x:x.max_ratio_others)[:limit]

	context = {
		'most_reliable': most_reliable,
		'fastest': fastest,
		'most_cooperative': most_cooperative,
		'best_interferer': best_interferer,
	}

	return render(request, 'front/halloffame.html', context)
