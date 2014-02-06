from rest_framework import serializers

from core.models import GameSession

class GameSessionSerialiser(serializers.ModelSerializer):
    class Meta:
        model = GameSession
        fields = ('turn_data', 'game_over', 'game_winner')
