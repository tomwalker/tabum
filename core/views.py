import json, random

from django.http import HttpResponseRedirect, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render_to_response
from django.template import RequestContext

from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response

from core.models import GameSession, OpenGame
from core.serialisers import GameSessionSerialiser
from core.permissions import IsNextToPlay
from core.tasks import normal_turn_process_store

from virus_player.models import Virus_player, virus_tech_tree
from health_player.models import Health_player, health_tech_tree

from countries.models import Map

from choices.models import ChoiceQuestion

# from engine.begin import normal_turn
# from engine.engine import Game_engine
# from engine.health import Health
# from engine.virus import Virus
# from engine.country import Country

def home_page(request):
    sample = random.sample(xrange(1,14), 3)
    return render_to_response('index.html',
                              locals(),
                              context_instance=RequestContext(request))

@login_required()
def players_mygames(request):
    games = GameSession.objects.filter(
        Q(virus_player=request.user) | Q(health_player=request.user))
    games_dict = {}

    for game in games:
        if game.virus_player == request.user:
            pa = "V"
            opponent = game.health_player.username
        else:
            pa = "H"
            opponent = game.virus_player.username
            
        if pa == game.next_to_play:
            status = 'to play'
        else:
            status = 'waiting'
        temp_dict = { 'id': game.id,
                      'status': status,
                      'turn_count': game.turn_count,
                      'playing_as': pa,
                      'opponent': opponent,
                      'finished': game.game_over,
                      'winner': game.game_winner}
        
        games_dict['game' + str(game.id)] = temp_dict
        
    return render_to_response('my-games.html', 
                                  locals(), 
                                  context_instance=RequestContext(request))

@login_required()
def new_game(request):
    """
    This will be remodelled later as a page to create an open game for players
    which is then displayed on an 'open games' page.
    """
    map_list = Map.objects.all()
    virus_list = Virus_player.objects.all()
    health_list = Health_player.objects.all()
    current_user = request.user

    return render_to_response('new-game.html',
                              locals(),
                              context_instance=RequestContext(request))


@login_required()
def create_open_game_invite(request):
    """
    Receives the details needed to make an open game invitation that other
    users can view and join.
    """
    if 'player' in request.GET and request.GET['player']:
        map_chosen = Map.objects.get(name = 'Earth')
        virus_chosen = Virus_player.objects.get(id = request.GET['virustype'])
        health_chosen = Health_player.objects.get(name = 'WHO')
        if request.GET['player_choice'] == 'virus':
            virus = User.objects.get(id = request.GET['player'])

            health = User.objects.get(username='open', email='open@games.com')

            new_open_game = OpenGame(virus_player=virus, health_player=health, map_chosen=map_chosen,
                                     virus_chosen=virus_chosen, health_chosen=health_chosen)
            new_open_game.save()
        # else:                   # useless now but may be useful later?
        #     health = User.objects.get(id = request.GET['player'])

        #     virus = User.objects.get(username='open', email='open@games.com')
            
        #     new_open_game = OpenGame(health_player=health, virus_player=virus, map_chosen=map_chosen,
        #                              virus_chosen=virus_chosen, health_chosen=health_chosen)
        #     new_open_game.save()

    return HttpResponseRedirect('/my-games/')

@login_required()
def open_games_list(request):
    """
    List all open games playing as the health player.
    Virus player starts games that are added to this list.
    """
    open_player = User.objects.get(username='open', email='open@games.com')
    # open_as_virus = OpenGame.objects.filter(virus_player = open_player)
    open_as_health = OpenGame.objects.filter(health_player = open_player)
    
    paginator = Paginator(open_as_health, 10) # Show 10 per page
    
    page = request.GET.get('page')
    try:
        games = paginator.page(page)
    except PageNotAnInteger:
        games = paginator.page(1)
    except EmptyPage:
        games = paginator.page(paginator.num_pages)
                
    return render_to_response('open-games.html', locals(), context_instance=RequestContext(request))

@login_required()
def open_games_view(request, pk=None):
    """
    View the details of an open game
    """
    open_game = OpenGame.objects.get(id=pk)
    return render_to_response('open-game-view.html', locals(), context_instance=RequestContext(request))

@login_required()
def open_game_accept(request):
    """
    Player accepts an open game
    """
    open_game = OpenGame.objects.get(id=request.GET['open_id'])
    if request.GET['accept_as'] == 'virus':
        virus = request.user
        health = open_game.health_player
    else:
        health = request.user
        virus = open_game.virus_player

    virus_chosen = open_game.virus_chosen
    health_chosen = open_game.health_chosen
    map_chosen = open_game.map_chosen
    open_game.delete()

    return first_turn(request, virus, health, virus_chosen, health_chosen, map_chosen)


# def create_game(request):
#     """
#     Starts a game manually, selecting all of the players etc
#     """
#     if 'virus' in request.GET and request.GET['virus']:
#         virus = User.objects.get(id = request.GET['virus'])
#         health = User.objects.get(id = request.GET['health'])
#         map_chosen = Map.objects.get(id = request.GET['map'])
#         virus_chosen = Virus_player.objects.get(id = request.GET['virustype'])
#         health_chosen = Health_player.objects.get(id = request.GET['healthtype']) 
#         return first_turn(request, virus, health, virus_chosen, health_chosen, map_chosen)

@login_required()
def first_turn(request, virus_player, health_player, virus_type, health_type, map_chosen):
    """
    After two players have joined a game.
    
    Create a new game session.
    
    Redirects to 'my games' afterwards.
    """
    new_game = GameSession.objects.create(virus_player=virus_player, 
                                          health_player=health_player)

    v = Virus_player.objects.get(agent = virus_type)
    v_json = v.stats_to_json()
    h = Health_player.objects.get(name = health_type)
    h_json = h.stats_to_json()
    c = Map.objects.filter(name = map_chosen)[0].to_json()
    vtt = virus_tech_tree.objects.get(agent = v).to_json()
    htt = health_tech_tree.objects.get(agency = h).to_json()

    v_turn_question_queryset = ChoiceQuestion.objects.filter(question_for = 'V')
    random_idx = random.randint(0, v_turn_question_queryset.count() - 1)
    random_q_id = v_turn_question_queryset[random_idx].id

    choice = ChoiceQuestion.objects.get(id = random_q_id).to_json()

    output = """
    {
    "countries": %s,
    "virus_player": %s,
    "virus_tech_tree": %s,  
    "health_player": %s,
    "health_tech_tree": %s,
    "turn_question": %s,
    "first_turn": true
    }
    """ % (c, v_json, vtt, h_json, htt, choice)

    # output = '{"pretend": { "json": "output", "one": 2}}' # test output
    new_game.set_turn_data(output, 'V')
    
    return HttpResponseRedirect('/my-games/')    

@login_required()
def submit_turn(request, game_session):
    """
    Takes the POST data from the request and calls the engine, passing the 
    necessary data from the request in with the turn_data from the last turn.

    Not called directly, but as a result of a POST request from angular app.
    
    Redirects to the 'my games'  page afterwards.

    input: request + GameSession object
    """
        
    # property_changes = request.POST.get('property_changes', '')
    virus_change = json.loads(request.DATA['virus_player'])
    virus_tt = json.loads(request.DATA['virus_tech'])
    health_change = json.loads(request.DATA['health_player'])
    health_tt = json.loads(request.DATA['health_tech'])
    health_change.pop("name", None) # remove name
    choice_outcome = request.DATA['choice_outcome']
    player_change = json.loads(request.DATA['change'])


    if game_session.virus_player == request.user:
        current_player = "V"
        next_to_play = "H"
    else:
        current_player = "H"
        next_to_play = "V"

    # load the players + countries as they were after last turn
    # v, h = load_players(game_session) not needed - data coming in from angular
    c = load_countries(game_session)

    if 'starting_from' in request.DATA:
        starting = request.DATA['starting_from']
        c['first_infection'] = starting


    #######################################################################
    # Below is the true version in which the engine is integrated
    #######################################################################

    if 'testing' not in request.DATA:

        if current_player == "V":
            change = {"virus_stats":  
                      { "properties": 
                        {"shift": player_change['shift'], "infectivity": player_change['infectivity'], 
                         "lethality": player_change['lethality'], "land_spread": player_change['land_spread'], 
                         "air_spread": player_change['air_spread'], "sea_spread": player_change['sea_spread']}
                        , "resistances":{}
                    },
                  "health_stats": 
                      {"teams" : 
                       {"field_researchers" : {}, "control_teams" : {},"cure_teams": {} },
                       "properties": 
                       {"disease_control": health_change['disease_control'], 
                        "virus_understanding" : health_change['virus_understanding'],  
                        "public_awareness": health_change['public_awareness']}
                   },
                      "next_to_play" : next_to_play
                    }
        if current_player == "H":
            frd = {}
            ctt = {}
            crt = {}
            for x in player_change['field_researchers_deployed']:
                frd[x] = 1
            for x in player_change['control_teams_deployed']:
                ctt[x] = 1
            for x in player_change['cure_teams_deployed']:
                crt[x] = 1
                
            change = {"virus_stats":  
                      { "properties": 
                        {"shift": 0, "infectivity": 0, 
                         "lethality": 0, "land_spread": 0, 
                         "air_spread": 0, "sea_spread": 0}
                        , "resistances":{}
                    },
                  "health_stats": 
                      {"teams" : 
                       {"field_researchers" : frd, 
                        "control_teams" : ctt,
                        "cure_teams": crt
                    },
                   "properties": 
                       {"disease_control": player_change['disease_control'], 
                        "virus_understanding" : player_change['virus_understanding'],  
                        "public_awareness": player_change['public_awareness']}
                   },
                      "next_to_play" : next_to_play
                  }
        
        if current_player == 'V':
                choices_blank = {'virus': choice_outcome, 'health': 0, 'country': {} }
        else:
                choices_blank = {'virus': 0, 'health': choice_outcome, 'country': {} }

        # below is for first turns of match
        if 'starting_from' in request.DATA and request.DATA['starting_from']:
            normal_turn_process_store.delay(virus_change, health_change, c, change, choices_blank, 
                                            True, game_session, next_to_play, virus_tt, health_tt)
        else:
            normal_turn_process_store.delay(virus_change, health_change, c, change, choices_blank, 
                                            False, game_session, next_to_play, virus_tt, health_tt)


    else:
    #######################################################################
    # BELOW JUST PUTS THE INPUT INTO TURN DATA, ONLY FOR TESTING
    #######################################################################
    # pass in the above + the outcome of the last turn
        if 'starting_from' in request.DATA:
            output = {}
            output['dog'] = request.DATA['starting_from']
        else:
            output = '{"pretend": { "json": "output", "one": 2}}' # test output

        game_session.set_turn_data(json.dumps(output), next_to_play)

    # end testing code

    
    return HttpResponseRedirect('/my-games/')

def load_countries(session):
    """
    Pass in a GameSession, returns a dict of the countries to use in the
    template.
    """
    return json.loads(session.turn_data)['countries']

def load_players(session):
    """
    Pass in a GameSession, returns a dict of the players to use in the 
    template.
    
    Returns two dicts - virus player, health player

    called by:
    virus_player, health_player = load_players(GameSession)
    """
    return json.loads(session.turn_data)['virus_player'],\
            json.loads(session.turn_data)['health_player']


def view_game(request, session_id=None):
    """
    View for viewing a game. Displays map and current game state.
    If logged in and your turn, lets you play.
    """
    if session_id == None and request.user.is_authenticated(): # needed? rethink
        return HttpResponseRedirect('/my-games/')
    if session_id == None and request.user.is_authenticated() != True:
        return HttpResponseRedirect('/')

    game = GameSession.objects.get(id=session_id)

    if request.method == 'POST':
        submit_turn(request, game)
    
    game_map = load_countries(game)
    next_to_play = game.next_to_play
    virus_player, health_player = load_players(game)

    if request.user.is_authenticated() and\
        (game.virus_player == request.user or\
         game.health_player == request.user):
            # logic for a player
            user_to_play = False
            if game.virus_player == request.user and game.next_to_play == 'V':
                user_to_play = True
            if game.health_player == request.user and game.next_to_play == 'H':
                user_to_play = True

            return render_to_response('map.html', 
                                  locals(), 
                                  context_instance=RequestContext(request))
            
    else:
        #logic for non player
        return render_to_response('map.html', 
                                  locals(), 
                                  context_instance=RequestContext(request))

class GameREST(APIView):
    """
    Retrieve or update a game.
    """
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsNextToPlay,)

    def get_object(self, pk):
        try:
            return GameSession.objects.get(id=pk)
        except GameSession.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        game = self.get_object(pk)
        serializer = GameSessionSerialiser(game)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        submit_turn(request, self.get_object(pk))

        return Response("complete")
