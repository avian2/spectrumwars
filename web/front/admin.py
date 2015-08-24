from django.contrib import admin
from front.models import Player, Game, PlayerResult, Round

class PlayerAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'user', 'enabled')
	list_filter = ('user', 'enabled')

class RoundAdmin(admin.ModelAdmin):
	list_display = ('id', 'started', 'nplayers', 'testbed', 'state')
	list_filter = ('testbed', 'state')

class GameAdmin(admin.ModelAdmin):
	list_display = ('id', 'duration', 'round')
	list_filter = ('round',)

admin.site.register(Player, PlayerAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(PlayerResult)
