from django.contrib.auth.models import User
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.template import RequestContext
from profiles.models import StatsUser

def my_profile(request):
    player = StatsUser.objects.get(user=request.user)

    if 'new_friend' in request.GET and request.GET['new_friend']:
        player.add_friend(StatsUser.objects.get(id = request.GET['new_friend']))

    wins = player.wins
    losses = player.losses
    premium = False
    friends = player.friends

    if request.user.groups.filter(name="Premium").exists():
        premium = True
    
    return render_to_response('my-profile.html', locals(), context_instance=RequestContext(request))

def player_profile(request, user_id=None):
    if user_id == None:
        return HttpResponseRedirect('/profile/')
    user_checked = User.objects.get(id = user_id)
    player = StatsUser.objects.get(user = user_checked)
    wins = player.wins
    losses = player.losses
    friends = player.friends
    premium = False
    accessing_user = request.user

    if user_checked.groups.filter(name="Premium").exists():
        premium = True
    
    return render_to_response('my-profile.html', locals(), context_instance=RequestContext(request))











