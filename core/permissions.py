import re
from rest_framework import permissions


class IsNextToPlay(permissions.BasePermission):
    """
    Custom permission to only allow the 'next to play' to GET and PUT
    """

    def has_permission(self, request, view):
        pk = re.search(r'\/([0-9]+)\/', request.path).group(1)
        game_session = view.get_object(pk)
        if game_session.next_to_play == 'V':
            if request.user == game_session.virus_player:
                return True
        if game_session.next_to_play == 'H':
            if request.user == game_session.health_player:
                return True
        return False










