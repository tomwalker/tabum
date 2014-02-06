import json

from django.core.urlresolvers import resolve
from django.http import HttpRequest

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, AnonymousUser

from django.test import TestCase
from django.test.client import Client, RequestFactory
from django.test.utils import override_settings

from rest_framework import status
from rest_framework.test import APIRequestFactory,force_authenticate


from core.factories import VirusUserFactory, HealthUserFactory,\
                           GameSessionFactory, CountryFactory, MapFactory,\
                           OpenGameFactory, HealthTypeFactory, VirusTypeFactory,\
                           VirusTechNodeFactory, VirusTechTreeFactory, \
                           HealthTechNodeFactory, HealthTechTreeFactory, \
                           ChoiceQuestionFactory, NewsItemFactory

from core.views import load_countries, open_game_accept,\
                       view_game, load_players, players_mygames,\
                       GameREST, first_turn, open_games_list, open_games_view,\
                       create_open_game_invite
                       

from core.models import GameSession, OpenGame

from core.tasks import normal_turn_process_store, create_news_items

from health_player.models import Health_player

global test_json_data_global

test_json_data_global = """
{
    "next_to_play": "V",
    "countries": {
        "china": {
            "population": {
                "healthy": 1400000000,
                "infected": 10,
                "dead": 1
            },
            "climate": "TEMPERATE",
            "healthcare": 4,
            "land_links": [
                "india",
                "nepal",
                "thailand",
                "korea",
                "japan"
            ],
            "air_links": [
                "USA",
                "japan",
                "spain"
            ],
            "sea_links": [
                "australia",
                "britain",
                "germany"
            ]
        },
        "paraguay": {
            "population": {
                "healthy": 1000000,
                "infected": 0,
                "dead": 0
            },
            "climate": "TROPICAL",
            "healthcare": 7,
            "land_links": [
                "india",
                "nepal",
                "thailand",
                "korea",
                "japan"
            ],
            "air_links": [
                "USA",
                "spain"
            ],
            "sea_links": [
                "australia",
                "britain",
                "germany"
            ]
        },
        "ireland": {
            "population": {
                "healthy": 432400,
                "infected": 488390,
                "dead": 90907930
            },
            "climate": "TEMPERATE",
            "healthcare": 7,
            "land_links": [
                "UK"
            ],
            "air_links": [
                "USA",
                "spain",
                "china"
            ],
            "sea_links": [
                "australia",
                "britain",
                "germany"
            ]
        }
    },
    "virus_player": {
        "agent": "HIV",
        "points": 50,
        "shift": 0.16,
        "infectivity": 4,
        "lethality": 7,
        "resistance": [
            "hot",
            "drug",
            "exam"
        ],
        "infected_countries": [
            "australia",
            "UK",
            "Indonesia"
        ],
        "air_spread": 3,
        "land_spread": 1,
        "sea_spread": 3
    },
    "health_player": {
        "points": 60,
        "field_researchers": {
            "africa": 1,
            "china": 3
        },
        "control_teams": {
            "UK": 1,
            "iceland": 3
        },
        "virus_understanding": 43,
        "cure_research": 20,
        "public_awareness": 70,
        "disease_control": 11
    }
}
"""



class MyGamesTest(TestCase):
    """
    Functional mygames page tests
    """
    def setUp(self):
        virus_user = VirusUserFactory()
        health_user = HealthUserFactory()
        test_session = GameSessionFactory(virus_player=virus_user,
                                          health_player=health_user)
        next_to_play = 'V'
        test_session.set_turn_data(test_json_data_global, next_to_play)

    def test_mygames_resolves(self):
        found = resolve('/my-games/')
        self.assertEqual(found.func, players_mygames)

    def test_view_game_resolves(self):
        found = resolve('/play/')
        self.assertEqual(found.func, view_game)
        
        client = Client()
        response = client.get('/play/1/')
        self.assertIn("Next to play", response.content.decode())


class TestGameSession(TestCase):

    def setUp(self):
        virus_user = VirusUserFactory()
        health_user = HealthUserFactory()
        test_session = GameSessionFactory(virus_player=virus_user,
                                          health_player=health_user)

    def test_setup_data(self):
        virus_user = get_user_model().objects.get(username='john')
        health_user = get_user_model().objects.get(username='ringo')
        self.assertEqual(virus_user.username, 'john')
        self.assertEqual(health_user.username, 'ringo')
        self.assertEqual(virus_user.email, 'lennon@thebeatles.com')
        self.assertEqual(health_user.email, 'ringo@thebeatles.com')
        
        test_session = GameSession.objects.get(virus_player=virus_user)
        self.assertEqual(test_session.health_player, health_user)
        self.assertEqual(test_session.turn_count, 0)
        
    def test_set_turn_data(self):
        virus_user = get_user_model().objects.get(username='john')
        health_user = get_user_model().objects.get(username='ringo')
        test_session = GameSession.objects.get(virus_player=virus_user)

        test_json_data = '{"turn_count": 3}'
        next_to_play = 'V'
        test_session.set_turn_data(test_json_data, next_to_play)
        self.assertEqual(test_session.turn_data, test_json_data)
        self.assertEqual(test_session.turn_count, 1)
        self.assertEqual(test_session.next_to_play, 'V')


class TestNormalGameTurn(TestCase):
    """
    Unit tests for views that handle a player turn.

    Input would be selections made by the player and his would be passed to 
    game engine.

    Response should pass any immediate outcome and render a template with 
    current game state.
    """
    
    def setUp(self):
        virus_user = VirusUserFactory()
        health_user = HealthUserFactory()
        
        virus_user2 = VirusUserFactory(username='Paul', 
                                        email='paul@thebeatles.com', 
                                        password='paulpassword')

        health_user2 = HealthUserFactory(username='george', 
                                        email='george@thebeatles.com', 
                                        password='georgepassword')

        test_session = GameSessionFactory(virus_player=virus_user,
                                          health_player=health_user)

        test_session2 = GameSessionFactory(virus_player=virus_user,
                                          health_player=health_user2)
        test_session2.set_turn_data({"cheese":"mouse"}, 'H')

        test_session3 = GameSessionFactory(virus_player=virus_user2,
                                           health_player=health_user2)    

        test_session4 = GameSessionFactory(virus_player=health_user,
                                           health_player=virus_user)

        china = CountryFactory()
        india = CountryFactory(name='India')
        map1 = MapFactory.create(countries=(china, india))

    def test_mygames_function(self):
        """
        Logged in user should see all current games, whether its their
        turn, turn count, whether they are virus or health for that game,

        Anon should redirect to signup
        """
        virus_user = get_user_model().objects.get(username='john')
        request = HttpRequest()
        request.user = virus_user
        response = players_mygames(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("waiting", response.content.decode())
        self.assertIn('Turn count', response.content.decode())
        self.assertIn("Playing As", response.content.decode())
        self.assertEqual(virus_user.games_as_virus_player.count(), 2)
        self.assertEqual(virus_user.games_as_health_player.count(), 1)

        # check that anon users are redirected
        factory = RequestFactory()
        request2 = factory.get('/my-games/')
        request2.user = AnonymousUser()
        response2 = players_mygames(request2)

        self.assertEqual(response2.status_code, 302)
        self.assertIn('register', response2.__getitem__('location'))


    def test_starting_new_game(self):
        """
        Should only call game engine if the virus is submitting as
        virus player is always first.
        """
        fungus = VirusTypeFactory(agent='fungus')
        parent_node = VirusTechNodeFactory(name='parent')
        anaemia = VirusTechNodeFactory()
        fever = VirusTechNodeFactory(name='fever')
        tree = VirusTechTreeFactory(agent=fungus, nodes=(anaemia, fever))

        who = Health_player.objects.create(name="WHO", 
                                     points=10, 
                                     field_researchers=1, 
                                     control_team=1, 
                                     virus_understanding=10, 
                                     cure_research=20, 
                                     public_awareness=30, 
                                     disease_control=40)

        research_node1 = HealthTechNodeFactory()
        research_node2 = HealthTechNodeFactory(name = 'more research')
        health_tree = HealthTechTreeFactory(agency = who,
                                            nodes = (research_node1,
                                                     research_node2))
        
        choice1 = ChoiceQuestionFactory()
        choice2 = ChoiceQuestionFactory(question_for = 'V',
                                        story = 'abc',
                                        question = '123',
                                        choice_1 = 'x',
                                        choice_2 = 'y',
                                        choice_1_value = '1',
                                        choice_2_value = '2')
        choice3 = ChoiceQuestionFactory(question_for = 'H',
                                        story = 'QWE',
                                        question = '123',
                                        choice_1 = 'x',
                                        choice_2 = 'y',
                                        choice_1_value = '1',
                                        choice_2_value = '2')
                                        
        
        health_user = get_user_model().objects.get(username='ringo')
        virus_user = get_user_model().objects.get(username='john')
        request = HttpRequest()
        request.user = virus_user
        request.method = 'POST'
        # request.POST['first_turn'] = 'first turn choices'
        request.POST['virus_type_chosen'] = 'Fungus'
        request.POST['map'] = 'earth'
        response = first_turn(request, virus_user, health_user, fungus.agent, who.name, 'earth' )

        # fake_turn_data = '{"pretend": { "json": "output", "one": 2}}'
        # v = Virus_player.objects.get(agent = fungus.agent)
        # h = Health_player.objects.get(name = who.name).stats_to_json()
        # c = Map.objects.get(name = request.POST['map']).to_json()
        # vtt = virus_tech_tree.objects.get(agent = v).to_json()
        
        # output = """
        # {
        # "countries": %s,
        # "virus_player": %s,
        # "health_player": %s,
        # "virus_tech_tree": %s,
        # "first_turn": true
        # }
        # """ % (c, v, h, vtt)


        new_game_session = GameSession.objects.get(id=5)

        self.assertEqual(new_game_session.next_to_play, 'V')
        self.assertIn("virus_tech_tree", new_game_session.turn_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/my-games/')


    def test_view_game_page_anon_or_nonplayer(self):
        """
        Displays the current game map.

        If its not your game then show map and stats
        """
        test_session = GameSession.objects.get(id=1)
        test_session.set_turn_data(test_json_data_global, 'H')

        request = HttpRequest()
        request.user = AnonymousUser()
        response = view_game(request, test_session.id)

        self.assertEqual(response.status_code, 200)
        self.assertIn('We are awaiting for the other player to play their turn',
                      response.content.decode())
        
        
    def test_view_game_page_player(self):
        """
        Displays the current game map.

        If logged in and its your turn, would let you play.

        If its your game and not your turn, shows current state of game.
        """
        test_session = GameSession.objects.get(id=1)
        test_session.set_turn_data(test_json_data_global, 'H')
        health_user = get_user_model().objects.get(username='ringo')
        virus_user = get_user_model().objects.get(username='john')        

        request = HttpRequest()
        request.user = health_user
        response = view_game(request, test_session.id)
        
        self.assertIn("health-google-chart", response.content.decode())
        
        request2 = HttpRequest()
        request2.user = virus_user
        response2 = view_game(request2, test_session.id)
        self.assertNotIn("health-google-chart", response2.content.decode())
        self.assertNotIn("google-chart", response2.content.decode())        


    def test_load_map(self):
        """
        For a GameSession, open up the turn data, extract the countries
        and return a dict for rendering 
        """
        test_session = GameSession.objects.get(id=1)
        test_session.set_turn_data(test_json_data_global, "V")

        response = load_countries(test_session)
        
        self.assertIn("paraguay", response)
        self.assertEqual(3, len(response.keys()))
        self.assertEqual("TEMPERATE", response['ireland']['climate'])
        self.assertEqual(1, response['china']['population']['dead'])

    def test_load_players(self):
        test_session = GameSession.objects.get(id=1)
        test_session.set_turn_data(test_json_data_global, "V")

        virus, health = load_players(test_session)
        
        self.assertIn("agent", virus)
        self.assertEqual(7, len(health.keys()))
        self.assertEqual(10, len(virus.keys()))
        self.assertIn("hot", virus['resistance'])
        self.assertEqual(1, health['control_teams']['UK'])

    def test_load_news_items(self):
        for x in range(1, 11):
            NewsItemFactory(story = str(x * 3), story_type = "N")

        NewsItemFactory(story = 'False story', story_type = "F")

        NewsItemFactory(story = 'True story', story_type = "T")

        countries = {'china': True, 'UK': True}
        output = {}
        output['countries'] = countries

        output['detected_infection'] = []
        no_detected_infection = create_news_items(output)

        self.assertEqual(len(no_detected_infection), 11)
        self.assertIn('False story'.upper(), no_detected_infection)

        output['detected_infection'] = ['china']
        detected_infection = create_news_items(output)
        self.assertEqual(len(detected_infection), 12)
        self.assertIn('True story'.upper(), detected_infection)

    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       CELERY_ALWAYS_EAGER=True,
                       BROKER_BACKEND='memory')
    def test_winning_turn(self):
        """
        Tests celery task for a winning game.

        Detects the presence of 'humanity' which is put in games
        that the virus player wins.

        The override decorator is needed for testing
        """
        test_session = GameSession.objects.get(id=1)
        test_session.set_turn_data(test_json_data_global, "V")
        
        virus_dict = {'shift': 0,
                      'land_spread': 0,
                      'resistance': ['hot', 'drug_resistance'],
                      'agent': 'HIV',
                      'infectivity': 0,
                      'points': 50,
                      'air_spread': 0,
                      'lethality': 0,
                      'sea_spread': 0}

        health_dict = {'virus_understanding': 0,
                       'cure_research': 0,
                       'field_researchers': 0,
                       'control_team': 0,
                       'disease_control': 0,
                       'points': 60,
                       'public_awareness': 0}

        country_dict_health_win = {'paraguay': {'climate': 'TROPICAL',
                                               'sea_links': ['ireland'],
                                               'land_links': ['china'],
                                               'healthcare': 7,
                                               'population': {'healthy': 100, 'infected': 0, 'dead': 0},
                                               'air_links': ['ireland'],
                                               'control_teams': 0,
                                               'research_teams': 0,
                                               'cure_teams': 0},
                                  'china': {'climate': 'TEMPERATE',
                                            'sea_links': ['ireland'],
                                            'land_links': ['paraguay'],
                                            'healthcare': 4,
                                            'population': {'healthy': 1000, 'infected': 0, 'dead': 0},
                                            'air_links': ['ireland'],
                                            'control_teams': 0,
                                            'research_teams': 0,
                                            'cure_teams': 0},
                                  'ireland': {'climate': 'TEMPERATE',
                                              'sea_links': ['china'],
                                              'land_links': ['paraguay'],
                                              'healthcare': 7,
                                              'population': {'healthy': 100, 'infected': 0, 'dead': 0},
                                              'air_links': ['china'],
                                              'control_teams': 0,
                                              'research_teams': 0,
                                              'cure_teams': 0}}

        country_dict_virus_win = {'paraguay': {'climate': 'TROPICAL',
                                                'sea_links': ['ireland'],
                                                'land_links': ['china'],
                                                'healthcare': 7,
                                                'population': {'healthy': 0, 'infected': 0, 'dead': 1},
                                                'air_links': ['ireland'],
                                                'control_teams': 0,
                                                'research_teams': 0,
                                                'cure_teams': 0},
                                   'china': {'climate': 'TEMPERATE',
                                             'sea_links': ['ireland'],
                                             'land_links': ['paraguay'],
                                             'healthcare': 4,
                                             'population': {'healthy': 0, 'infected': 0, 'dead': 1},
                                             'air_links': ['ireland'],
                                             'control_teams': 0,
                                             'research_teams': 0,
                                             'cure_teams': 0},
                                   'ireland': {'climate': 'TEMPERATE',
                                               'sea_links': ['china'],
                                               'land_links': ['paraguay'],
                                               'healthcare': 7,
                                               'population': {'healthy': 0, 'infected': 0, 'dead': 10000},
                                               'air_links': ['china'],
                                               'control_teams': 0,
                                               'research_teams': 0,
                                               'cure_teams': 0}}        
                        
    
        session = json.loads(test_json_data_global)
        change = {"virus_stats":  
                  { "properties": 
                    {"shift": 0, "infectivity": 0, 
                     "lethality": 0, "land_spread": 0, 
                     "air_spread": 0, "sea_spread": 0}
                    , "resistances":{}
                  },
                  "health_stats": 
                  {"teams" : 
                   {"field_researchers" : "", 
                    "control_teams" : "",
                    "cure_teams": ""
                  },
                  "properties": 
                   {"disease_control": session['health_player']['disease_control'], 
                    "virus_understanding" : session['health_player']['virus_understanding'],  
                    "public_awareness": session['health_player']['public_awareness']}
                  },
                  "next_to_play" : session['next_to_play'] }

        choices_blank = {'virus': 0, 'health': 0, 'country': {} }

        self.assertFalse(test_session.game_over) # game active before
        
        normal_turn_process_store(virus_dict, health_dict, country_dict_health_win, change, choices_blank,
                                  False, test_session, 'V', '', '')

        self.assertIn('eradicated', test_session.turn_data) # health win
        self.assertEqual(test_session.game_winner, 'H')
        self.assertTrue(test_session.game_over) # game over afterwards

        test_session.set_turn_data(test_json_data_global, "H")
        virus_dict = {'shift': 0,
                      'land_spread': 0,
                      'resistance': ['hot', 'drug_resistance'],
                      'agent': 'HIV',
                      'infectivity': 0,
                      'points': 50,
                      'air_spread': 0,
                      'lethality': 0,
                      'sea_spread': 0}        

        normal_turn_process_store(virus_dict, health_dict, country_dict_virus_win, change, choices_blank,
                                  False, test_session, 'H', '', '')

        self.assertIn('humanity', test_session.turn_data)
        self.assertEqual(test_session.game_winner, 'V')
        self.assertTrue(test_session.game_over)        

class TestRESTapi(TestCase):
    """
    Unit tests relating to the REST api used to communicate with
    angular app which will handle game map.
    
    Only returns for signed in users, for their game only and when
    it is their turn.
    """
    
    def setUp(self):
        virus_user = VirusUserFactory()
        health_user = HealthUserFactory()
        
        virus_user2 = VirusUserFactory(username='Paul', 
                                        email='paul@thebeatles.com', 
                                        password='paulpassword')

        health_user2 = HealthUserFactory(username='george', 
                                        email='george@thebeatles.com', 
                                        password='georgepassword')

        test_session = GameSessionFactory(virus_player=virus_user,
                                          health_player=health_user)
        
        choice1 = ChoiceQuestionFactory()
        choice2 = ChoiceQuestionFactory(question_for = 'V',
                                        story = 'abc',
                                        question = '123',
                                        choice_1 = 'x',
                                        choice_2 = 'y',
                                        choice_1_value = '1',
                                        choice_2_value = '2')
        choice3 = ChoiceQuestionFactory(question_for = 'H',
                                        story = 'QWE',
                                        question = '123',
                                        choice_1 = 'x',
                                        choice_2 = 'y',
                                        choice_1_value = '1',
                                        choice_2_value = '2')

    def test_get_game_data_player(self):
        """
        Should return game session data for authenticated user upon GET
        request to /play/<session_id>/ag

        Should only return when its that users turn to play.
        """
        test_session = GameSession.objects.get(id=1)
        test_session.set_turn_data(test_json_data_global, "V")

        factory = APIRequestFactory()
        user = User.objects.get(username='john')
        view = GameREST.as_view()
        url = 'play/' + str(test_session.id) + '/ag/'
        request = factory.get(url)
        force_authenticate(request, user=user)
        response = view(request, test_session.id)

        self.assertEqual(response.data['turn_data'], test_json_data_global)
        
        # This test is not the user that should play next
        user2 = User.objects.get(username='ringo')
        request2 = factory.get(url)
        force_authenticate(request2, user=user2)
        response2 = view(request2, test_session.id)
        
        self.assertEqual(response2.data['detail'], 
                         'You do not have permission to perform this action.')


    def test_post_game_data(self):
        """
        Post output of game return back to django.
        Authenticated user on their turn only.
        Same url as get: /play/<session_id>/ag
        """
        test_session = GameSession.objects.get(id=1)
        test_session.set_turn_data(test_json_data_global, "V")

        factory = APIRequestFactory()
        user = User.objects.get(username='john')
        view = GameREST.as_view()
        url = 'play/' + str(test_session.id) + '/ag/'
        request = factory.post(url, {'virus_player': '{"test": 1}',
                                     'health_player': '{"test2": 2}',
                                     'testing': True,
                                     'choice_outcome': '{"test3": 3}',
                                     'virus_tech': '{"dog": 1}',
                                     'health_tech': '{"cat": 2}',
                                     'change': '{"frog": "monkey"}'
                                     }, format='json')
        force_authenticate(request, user=user)

        response = view(request, test_session.id)
        
        # for the tests, reload the session from the DB
        test_session = GameSession.objects.get(id=1)
        self.assertNotEqual(response.data, test_json_data_global)
        self.assertEqual(response.data, 'complete')
        self.assertEqual(test_session.turn_data, json.dumps('{"pretend": { "json": "output", "one": 2}}') )
        self.assertEqual(test_session.next_to_play, 'H')

    def test_post_first_turn(self):
        """
        Post output of game return back to django.
        Authenticated user on their turn only.
        Same url as get: /play/<session_id>/ag
        """
        test_session = GameSession.objects.get(id=1)
        test_session.set_turn_data(test_json_data_global, "V")

        factory = APIRequestFactory()
        user = User.objects.get(username='john')
        view = GameREST.as_view()
        url = 'play/' + str(test_session.id) + '/ag/'
        request = factory.post(url, {'virus_player': '{"test": 1}',
                                     'health_player': '{"test2": 2}',
                                     'starting_from': 'india',
                                     'testing': True,
                                     'choice_outcome': '{"test3": 3}',
                                     'virus_tech': '{"dog": 1}',
                                     'health_tech': '{"cat": 2}',
                                     'change': '{"frog": "monkey"}'
                                     }, format='json')
        force_authenticate(request, user=user)

        response = view(request, test_session.id)
        
        # for the tests, reload the session from the DB
        test_session = GameSession.objects.get(id=1)
        self.assertNotEqual(response.data, test_json_data_global)
        self.assertEqual(response.data, 'complete')
        self.assertEqual(test_session.turn_data, '{"dog": "india"}')
        self.assertEqual(test_session.next_to_play, 'H')

    def test_denial_for_other_requests(self):
        """
        Prevent anything but the requests tested in the above tests.
        
        Anon user, logged in but wrong game, logged in & their game but
        not their turn,
        """
        test_session = GameSession.objects.get(id=1)
        test_session.set_turn_data(test_json_data_global, "V")
        
        # anon first
        factory = APIRequestFactory()
        user = AnonymousUser()
        view = GameREST.as_view()
        url = 'play/' + str(test_session.id) + '/ag/'
        request = factory.post(url, {'property_changes': 'test',
                                     'choice_outcome': 'test2'})
        force_authenticate(request, user=user)
        response = view(request, test_session.id)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # logged in but wrong game
        factory = APIRequestFactory()
        user = User.objects.get(username='Paul')
        view = GameREST.as_view()
        url = 'play/' + str(test_session.id) + '/ag/'
        request = factory.post(url, {'property_changes': 'test',
                                     'choice_outcome': 'test2'})
        force_authenticate(request, user=user)
        response = view(request, test_session.id)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # logged in, their game, not their turn
        factory = APIRequestFactory()
        user = User.objects.get(username='ringo')
        view = GameREST.as_view()
        url = 'play/' + str(test_session.id) + '/ag/'
        request = factory.post(url, {'property_changes': 'test',
                                     'choice_outcome': 'test2'})
        force_authenticate(request, user=user)
        response = view(request, test_session.id)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class Test_Open_Game(TestCase):
    """
    Unit tests for creating open games
    """

    def setUp(self):
        virus_user = VirusUserFactory()
        open_user = HealthUserFactory(username='open', email='open@games.com')
        health_user = HealthUserFactory()
        TestOpen = OpenGameFactory(virus_player=virus_user,
                                   health_player=health_user)
        TestWaiting = OpenGameFactory(virus_player=virus_user,
                                      health_player=open_user)
        fungus = VirusTypeFactory()
        WHO = HealthTypeFactory()
        china = CountryFactory()
        india = CountryFactory(name='India')
        map1 = MapFactory.create(countries=(china, india))

        anaemia = VirusTechNodeFactory()
        fever = VirusTechNodeFactory(name='fever')
        tree = VirusTechTreeFactory(agent=fungus, nodes=(anaemia, fever))

        research_node1 = HealthTechNodeFactory()
        research_node2 = HealthTechNodeFactory(name = 'more research')
        health_tree = HealthTechTreeFactory(agency = WHO,
                                            nodes = (research_node1,
                                                     research_node2))        
        choice1 = ChoiceQuestionFactory()
        choice2 = ChoiceQuestionFactory(question_for = 'V',
                                        story = 'abc',
                                        question = '123',
                                        choice_1 = 'x',
                                        choice_2 = 'y',
                                        choice_1_value = '1',
                                        choice_2_value = '2')
        choice3 = ChoiceQuestionFactory(question_for = 'H',
                                        story = 'QWE',
                                        question = '123',
                                        choice_1 = 'x',
                                        choice_2 = 'y',
                                        choice_1_value = '1',
                                        choice_2_value = '2')        
        
    def create_open_game_model(self):
        virus_user = get_user_model().objects.get(username='john')
        test_open_game = OpenGame.objects.get(virus_player=virus_user)

        self.assertEqual(test_open_game.map_chosen.name, 'earth')
        self.assertEqual(test_open_game.virus_chosen.agent, 'HIV')
        self.assertEqual(test_open_game.health_chosen.name, 'WHO')


    def create_open_game_view_invite(self):
        health_user = get_user_model().objects.get(username='ringo')
        virus_user = get_user_model().objects.get(username='john')
        request = HttpRequest()
        request.method = 'POST'
        request.POST['virustype'] = 1
        request.POST['map'] = 1
        request.POST['healthtype'] = 1
        request.POST['player_choice'] = 'virus'
        request.POST['player'] = virus_user.id
        response = create_open_game_invite(request)

        new_open_game_invite = OpenGame.objects.get(id=1)

        self.assertEqual(new_open_game_invite.virus_player, virus_user)
        self.assertEqual(new_open_game_invite.map_chosen.name, 'earth')
        self.assertEqual(new_open_game_invite.virus_chosen.agent, 'HIV')
        self.assertEqual(new_open_game_invite.health_chosen.name, 'cheese')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/my-games/')        

    def test_open_games_list(self):
        virus_user = get_user_model().objects.get(username='john')
        request = HttpRequest()
        request.user = virus_user
        response = open_games_list(request)

        # only 1 game, no pagination needed
        self.assertIn('john', response.content)
        self.assertIn('HIV', response.content)
        self.assertIn('view game', response.content)
        self.assertNotIn('Next', response.content)

        # add 20 other open games
        virus_user = get_user_model().objects.get(username='john')
        open_user = get_user_model().objects.get(username='open')
        for x in range(20):
            OpenGameFactory(virus_player = virus_user,
                            health_player = open_user)
        response = open_games_list(request)
        
        # Pagination needed
        self.assertIn('Next', response.content)

    def test_open_games_view(self):
        virus_user = get_user_model().objects.get(username='john')
        request = HttpRequest()
        request.user = virus_user        
        response = open_games_view(request, 1)

        self.assertIn('HIV', response.content)
        self.assertIn('earth', response.content)
        self.assertIn('WHO', response.content)

    def test_open_game_accept(self):
        factory = RequestFactory()
        user = User.objects.create_user(username = 'steve',
                                             email = 's@s.com',
                                             password = 'steve')

        self.assertEqual(GameSession.objects.count(), 0) # no game sessions
        
        request = factory.get('/accept-open-game-invite/',
                                   {'accept_as': 'virus', 'open_id': 1},
                                   follow = False)

        request.user = user

        response = open_game_accept(request)
        s = GameSession.objects.get(virus_player = user)

        self.assertEqual(GameSession.objects.count(), 1) # new session
        self.assertEqual(s.virus_player, user)
        self.assertEqual(response.status_code, 302) # redirect to my games
