from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django import forms


from front.models import Player

class PlayerForm(forms.ModelForm):
	class Meta:
		model = Player
		fields = ['name', 'code']

@login_required
def index(request):
	player_list = Player.objects.all()

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

	context = {
		'player': player,
		'user': request.user,
	}

	return render(request, 'front/player.html', context)

@login_required
def player_del(request, id):
	player = get_object_or_404(Player, pk=id)

	if request.method == 'POST':
		player.delete()

	return HttpResponseRedirect(reverse('index'))