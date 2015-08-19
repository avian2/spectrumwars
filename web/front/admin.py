from django.contrib import admin
from front.models import Player, Game, PlayerResult, Round

admin.site.register(Player)
admin.site.register(Round)
admin.site.register(Game)
admin.site.register(PlayerResult)
