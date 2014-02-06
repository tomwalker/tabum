from django.contrib.auth.models import Group
from django.db import models
from django.conf import settings



class StatsUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)

    wins = models.PositiveIntegerField(null=False, blank=False, default=0)
    losses = models.PositiveIntegerField(null=False, blank=False, default=0)

    friends = models.ManyToManyField('self', blank=True,)

    # objects = StatsUserManager()

    def add_friend(self, friend):
        self.friends.add(friend)
        self.save()

    def make_premium_member(self):
        Group.objects.get_or_create(name="Premium")
        g = Group.objects.get(name="Premium")
        self.user.groups.add(g)

    def __unicode__(self):
        return self.user.username


    class Meta:
        verbose_name = "User profile"
        verbose_name_plural = "User profiles"
