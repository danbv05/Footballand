from django.contrib import admin
from .models import League, Player, Match, Bet, Footballteam, Prize

admin.site.register(League)
admin.site.register(Bet)
admin.site.register(Player)
admin.site.register(Match)
admin.site.register(Footballteam)
admin.site.register(Prize)
