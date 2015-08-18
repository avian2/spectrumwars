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

		avgratio /= alln
		crashratio = float(crashn)/alln

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
