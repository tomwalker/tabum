from django.db import models
from django.conf import settings

from core.validators import validate_json

from countries.models import Map

from virus_player.models import Virus_player

from health_player.models import Health_player

class GameSession(models.Model):
    virus_player = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                     related_name='games_as_virus_player')

    health_player = models.ForeignKey(settings.AUTH_USER_MODEL,
                                      related_name='games_as_health_player')

    """
    The above allow you to get the following querysets:
        user.games_as_virus_player.all()
        user.games_as_virus_player.count()
        etc.
    """

    turn_count = models.PositiveSmallIntegerField(default=0, editable=False)
    
    turn_data = models.TextField(editable=True,validators=[validate_json])

    CURRENT_PLAYER_CHOICES = ( ('V', 'Virus player'), ('H', 'Healthy player'))

    next_to_play = models.CharField(max_length=1, choices=CURRENT_PLAYER_CHOICES, default='V')

    game_over = models.BooleanField(default = False)

    game_winner = models.CharField(blank = True,
                                   max_length = 1,
                                   choices = CURRENT_PLAYER_CHOICES)

    def set_turn_data(self, data, next_to_play):
        self.turn_data = data
        self.turn_count += 1
        self.next_to_play = next_to_play
        self.save()

    def finish_game(self, winner):
        self.game_over = True
        self.game_winner = winner
        self.save()


class OpenGame(models.Model):
    virus_player = models.ForeignKey(settings.AUTH_USER_MODEL,
                                     blank=True,
                                     related_name='open_games_as_virus_player')

    health_player = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                      blank=True, 
                                      related_name='open_games_as_health_player')

    map_chosen = models.ForeignKey(Map, blank=False)

    virus_chosen = models.ForeignKey(Virus_player, blank=False)

    health_chosen = models.ForeignKey(Health_player, blank=True)
