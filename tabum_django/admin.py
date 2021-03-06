from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple


from core.models import GameSession, OpenGame
from core.serialisers import GameSessionSerialiser
from core.permissions import IsNextToPlay

from virus_player.models import Virus_player, virus_tech_tree_node, virus_tech_tree
from health_player.models import Health_player, health_tech_tree_node, health_tech_tree

from countries.models import Map, Country

from profiles.models import StatsUser

from choices.models import ChoiceQuestion

from news_feed.models import NewsItem


class MapAdmin(admin.ModelAdmin):
    list_display = ('name', )
    filter_horizontal = ('countries', )


class SessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'virus_player', 'health_player', 'next_to_play'] 

class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('land_links', 'air_links', 'sea_links', )

class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('story', 'story_type')
    list_filter = ('story_type',)

class StatsUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'group_memberships')
    search_fields = ('user__username',)
    
    def group_memberships(self, obj):
        """
        get group, separate by comma,
        and display empty string if user has no group
        """
        return ','.join([g.name for g in obj.user.groups.all()]) if obj.user.groups.count() else ''
    


admin.site.register(GameSession, SessionAdmin)
admin.site.register(Map, MapAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Virus_player)
admin.site.register(virus_tech_tree)
admin.site.register(virus_tech_tree_node)
admin.site.register(Health_player)
admin.site.register(health_tech_tree)
admin.site.register(health_tech_tree_node)
admin.site.register(OpenGame)
admin.site.register(StatsUser, StatsUserAdmin)
admin.site.register(ChoiceQuestion)
admin.site.register(NewsItem, NewsItemAdmin)
