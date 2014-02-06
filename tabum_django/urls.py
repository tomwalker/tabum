from django.conf.urls import patterns, include, url
from django.conf import settings # remove for production
from django.conf.urls.static import static # remove static in production
from django.views.generic import TemplateView

from rest_framework.urlpatterns import format_suffix_patterns
from core.views import GameREST
from postman.views import (InboxView, SentView, ArchivesView, TrashView,
                           WriteView, ReplyView, MessageView, ConversationView,
                           ArchiveView, DeleteView, UndeleteView)
from postman import OPTIONS

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    # normal pages handled by django
    url(r'^$', 'core.views.home_page', name='home'),
    # url(r'^$', TemplateView.as_view(template_name='index.html'), name="home"),

    url(r'^my-games/$', 'core.views.players_mygames', name='my_games'),

    url(r'^play/$', 'core.views.view_game', name='game_page'),    

    # making and accepting games
    url(r'^new-game/$', 'core.views.new_game', name='new_game'),
                       
    url(r'^create-open-game-invite/$', 'core.views.create_open_game_invite',
        name='open_game_invite'),
                       
    url(r'^accept-open-game-invite/$', 'core.views.open_game_accept',
        name='open_game_accept'),
                       
    url(r'^open-games/$', 'core.views.open_games_list', name='open_games_list'),
                       
    url(r'^open-games/(?P<pk>[0-9]+)$', 'core.views.open_games_view', name='open_games_view'),

    # load up a game by the session id
    url(r'^play/(?P<session_id>\d+)/$', 'core.views.view_game', name='play_game'),  
    
    # REST api calls
    url(r'^r/(?P<pk>[0-9]+)$', GameREST.as_view()),
    url(r'^r/(?P<pk>[0-9]+)$', GameREST.as_view()),

    # player profile and related
    url(r'^profile/$', 'profiles.views.my_profile', name='my_profile'),
    url(r'^profile/(?P<user_id>\d+)/$', 'profiles.views.player_profile', name='player_profile'),  

    # the below is for django-registration app. 
    # Login is at tabum.org/profile/login, registration is tabum.org/profile/register etc.
    # url(r'^profile/', include('registration.backends.default.urls')),
    url(r'^profile/', include('profiles.registration_urls')),
    url(r'^profile/logout/$', 'django.contrib.auth.views.logout', name='logout'),
    
    # below is for django-postman, used for messaging, url is at tabum.org/profile/messages
    # url(r'^profile/messages/', include('postman.urls')),

    url(r'^admin/', include(admin.site.urls)),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # remove for production
urlpatterns = format_suffix_patterns(urlpatterns)

    # below are custom templates for postman
    

urlpatterns += patterns('postman.views',

    url(r'^profile/messages/inbox/(?:(?P<option>'+OPTIONS+')/)?$',
        InboxView.as_view(template_name='postman/postman/t_inbox.html'),
        name='postman_inbox'),
                        
    url(r'^profile/messages/sent/(?:(?P<option>'+OPTIONS+')/)?$',
        SentView.as_view(), name='postman_sent'),

    # url(r'^profile/messages/archives/(?:(?P<option>'+OPTIONS+')/)?$',
    #     ArchivesView.as_view(), name='postman_archives'),
                        
    # url(r'^profile/messages/trash/(?:(?P<option>'+OPTIONS+')/)?$',
    #     TrashView.as_view(), name='postman_trash'),
                        
    url(r'^profile/messages/write/(?:(?P<recipients>[\w.@+-:]+)/)?$',
        WriteView.as_view(template_name='postman/postman/write.html'),
        name='postman_write'),
                        
    url(r'^profile/messages/reply/(?P<message_id>[\d]+)/$',
        ReplyView.as_view(), name='postman_reply'),
                        
    url(r'^profile/messages/view/(?P<message_id>[\d]+)/$',
        MessageView.as_view(template_name='postman/postman/view.html'),
        name='postman_view'),
                        
    url(r'^profile/messages/view/t/(?P<thread_id>[\d]+)/$',
        ConversationView.as_view(template_name='postman/postman/view.html'),
        name='postman_view_conversation'),
                        
    url(r'^profile/messages/archive/$',
        ArchiveView.as_view(), name='postman_archive'),
                        
    url(r'^profile/messages/delete/$',
        DeleteView.as_view(), name='postman_delete'),
                        
    url(r'^profile/messages/undelete/$',
        UndeleteView.as_view(), name='postman_undelete'),

)
