from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User
from django.http import HttpRequest
from django.test import TestCase

from profiles.models import StatsUser
from profiles.views import my_profile, player_profile

class TestUserModel(TestCase):
    def setUp(self):
        User.objects.create_user(username="keith_test", 
                                 email="keith@tabum.com", 
                                 password="keiths_password", )

    
    def test_setup_data(self):
        keith = auth.authenticate(username="keith_test", 
                                  password='keiths_password')
        self.assertEqual(keith.username, "keith_test")
        self.assertEqual(keith.email, "keith@tabum.com")
        self.assertEqual(keith.id, 1)

    def test_wins_losses(self):
        keith = auth.authenticate(username="keith_test", 
                                  password='keiths_password')
        StatsUser.objects.create(user=keith)
        keith_profile = StatsUser.objects.get(user=keith)
        self.assertEqual(keith_profile.wins, 0)
        self.assertEqual(keith_profile.losses, 0)
        keith_profile.wins = 5
        keith_profile.losses = 10
        self.assertEqual(keith_profile.wins, 5)
        self.assertEqual(keith_profile.losses, 10)
        keith_profile.wins = 88394283
        keith_profile.losses = 107743724738
        self.assertEqual(keith_profile.wins, 88394283)
        self.assertEqual(keith_profile.losses, 107743724738)

    def test_multiple_players(self):
        keith = auth.authenticate(username="keith_test", 
                                  password='keiths_password')
        dave = User.objects.create_user(username="dave_test", 
                                        email="dave@tabum.com", 
                                        password="daves_password", )
        self.assertEqual(dave.username, "dave_test")
        self.assertEqual(dave.email, "dave@tabum.com")
        self.assertEqual(dave.id, 2)

    def test_groups(self):
        Group.objects.get_or_create(name="Premium")
        g = Group.objects.get(name="Premium")

        keith = auth.authenticate(username="keith_test", 
                                  password='keiths_password')
        keith.groups.add(g)
        self.assertTrue(g in keith.groups.all())

    def test_make_premium(self):
        keith = auth.authenticate(username="keith_test", 
                                  password='keiths_password')
        StatsUser.objects.create(user=keith)
        keith_profile = StatsUser.objects.get(user=keith)
        keith_profile.make_premium_member()
        g = Group.objects.get(name="Premium")
        self.assertTrue(g in keith.groups.all())

class TestUserViews(TestCase):
    def setUp(self):
        keith = User.objects.create_user(username="keith_test", 
                                 email="keith@tabum.com", 
                                 password="keiths_password", )
        StatsUser.objects.create(user=keith)
        dave = User.objects.create_user(username="dave_test", 
                                 email="dave@tabum.com", 
                                 password="daves_password", )
        StatsUser.objects.create(user=dave)        

    def test_own_profile(self):
        user_keith = get_user_model().objects.get(username='keith_test')
        request = HttpRequest()
        request.user = user_keith
        response = my_profile(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Wins', response.content.decode())
        self.assertIn('keith_test', response.content.decode())

    def test_other_profiles(self):
        user_keith = get_user_model().objects.get(username='keith_test')
        user_dave = get_user_model().objects.get(username='dave_test')
        request = HttpRequest()
        request.user = user_keith
        response = player_profile(request, user_dave.id)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Wins', response.content.decode())
        self.assertIn('Write to dave_test', response.content.decode())
        self.assertIn('dave_test', response.content.decode())










