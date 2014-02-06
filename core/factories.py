from django.contrib.auth.models import User

from core.models import GameSession, OpenGame
from countries.models import Map, Country
from virus_player.models import Virus_player, virus_tech_tree, virus_tech_tree_node
from health_player.models import Health_player, health_tech_tree, health_tech_tree_node
from choices.models import ChoiceQuestion
from news_feed.models import NewsItem

import factory

class VirusUserFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = User
    FACTORY_DJANGO_GET_OR_CREATE = ('username', 'email', 'password',)

    username = 'john'
    email = 'lennon@thebeatles.com'
    password = 'johnpassword'

class HealthUserFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = User
    FACTORY_DJANGO_GET_OR_CREATE = ('username', 'email', 'password',)

    username = 'ringo'
    email = 'ringo@thebeatles.com'
    password = 'ringopassword'

class GameSessionFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = GameSession
    FACTORY_DJANGO_GET_OR_CREATE = ('virus_player', 'health_player',)

    virus_player = factory.SubFactory(VirusUserFactory)
    health_player = factory.SubFactory(HealthUserFactory)

class MapFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Map
#    FACTORY_DJANGO_GET_OR_CREATE = ('name')

    name = 'earth'

    @factory.post_generation
    def countries(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for country in extracted:
                self.countries.add(country)


class CountryFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Country
    FACTORY_DJANGO_GET_OR_CREATE = ('name', 'population', 'climate', 'healthcare')

    name = 'China'
    population = 1400000000
    climate = 'TEMPERATE'
    healthcare = 4

    
class HealthTypeFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Health_player
    FACTORY_DJANGO_GET_OR_CREATE = ('name', 'points', 'field_researchers',
                                    'control_team', 'virus_understanding',
                                    'cure_research', 'public_awareness',
                                    'disease_control')

    name = 'WHO'
    points = 5
    field_researchers = 1
    control_team = 0
    virus_understanding = 0
    cure_research = 0
    public_awareness = 0
    disease_control = 0


class VirusTypeFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Virus_player
    FACTORY_DJANGO_GET_OR_CREATE = ('agent', 'points', 'shift',
                                    'infectivity', 'lethality',
                                    'air_spread', 'land_spread',
                                    'sea_spread', 'resistance')

    agent = 'HIV'
    points = 5
    shift = 1
    infectivity = 10
    lethality = 5
    air_spread = 10
    land_spread = 80
    sea_spread = 40
    resistance = 'CD'


class OpenGameFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = OpenGame
    FACTORY_DJANGO_GET_OR_CREATE = ('virus_player', 'health_player', 'map_chosen', 
                                    'virus_chosen', 'health_chosen')

    virus_player = factory.SubFactory(VirusUserFactory)
    health_player = factory.SubFactory(HealthUserFactory)
    map_chosen = factory.SubFactory(MapFactory)
    virus_chosen = factory.SubFactory(VirusTypeFactory)
    health_chosen = factory.SubFactory(HealthTypeFactory)

class VirusTechNodeFactory(factory.DjangoModelFactory):
    FACTORY_FOR = virus_tech_tree_node
    FACTORY_DJANGO_GET_OR_CREATE = ('name', 'display_active', 'display_inactive', 'active')

    name = 'anaemia'
    display_inactive = 'off'
    display_active = 'on'
    # parent = virus_tech_tree_node.objects.get(name='parent')
    active = False
    selectable = True
    cost = 10
    # requires = ''
    effect_on_infectivity = 0
    effect_on_lethality = 0
    effect_on_shift = 0
    effect_on_land_spread = 0
    effect_on_sea_spread = 0
    effect_on_air_spread = 0
    
class VirusTechTreeFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = virus_tech_tree
    
    agent = factory.SubFactory(VirusTypeFactory)

    @factory.post_generation
    def nodes(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for node in extracted:
                self.nodes.add(node)

class HealthTechNodeFactory(factory.DjangoModelFactory):
    FACTORY_FOR = health_tech_tree_node
    FACTORY_DJANGO_GET_OR_CREATE = ('name', 'display_active', 'display_inactive', 'active')

    name = 'cure'
    display_inactive = 'off'
    display_active = 'on'
    # parent = virus_tech_tree_node.objects.get(name='parent')
    active = False
    selectable = True
    cost = 10
    # requires = ''
    effect_on_field_researchers = 0
    effect_on_control_teams = 0
    effect_on_virus_understanding = 0
    effect_on_cure_research = 0
    effect_on_public_awareness = 0
    effect_on_disease_control = 0
    
class HealthTechTreeFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = health_tech_tree
    
    agency = factory.SubFactory(HealthTypeFactory)

    @factory.post_generation
    def nodes(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for node in extracted:
                self.nodes.add(node)

class ChoiceQuestionFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = ChoiceQuestion
    FACTORY_DJANGO_GET_OR_CREATE = ('question_for', 'story', 'question', 'choice_1', 'choice_2', 'choice_1_value', 'choice_2_value',)

    question_for = 'V'
    story = 'Once upon a time'
    question = 'What is your favourite colour?'
    choice_1 = 'red'
    choice_2 = 'blue'    
    choice_1_value = 1
    choice_2_value = 2

class NewsItemFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = NewsItem
    FACTORY_DJANGO_GET_OR_CREATE = ('story', 'story_type')

    story = 'In the beginning...'
    story_type = 'N'










