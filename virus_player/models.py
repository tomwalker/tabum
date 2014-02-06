import json

from django.db import models

from django.core.validators import MinValueValidator, MaxValueValidator

class Virus_player(models.Model):
    agent = models.CharField(blank=False, max_length=256)

    description = models.TextField(blank = True)

    avatar = models.ImageField(upload_to = 'virus_avatar/', blank = True)

    points = models.PositiveIntegerField(blank=False, default=10)

    shift = models.PositiveIntegerField(blank=False, 
                                        default=1, 
                                        validators=[MaxValueValidator(100), MinValueValidator(0)],
                                        help_text="Value between 0 and 100", )

    infectivity = models.PositiveIntegerField(blank=False, 
                                              validators=[MaxValueValidator(100),
                                                          MinValueValidator(1)],
                                              help_text="1 to 100",)
    lethality = models.PositiveIntegerField(blank=False, 
                                              validators=[MaxValueValidator(100),
                                                          MinValueValidator(1)],
                                              help_text="1 to 100",)

    air_spread = models.PositiveIntegerField(blank=False, 
                                              validators=[MaxValueValidator(100),
                                                          MinValueValidator(1)],
                                              help_text="1 to 100",)
    land_spread = models.PositiveIntegerField(blank=False, 
                                              validators=[MaxValueValidator(100),
                                                          MinValueValidator(1)],
                                              help_text="1 to 100",)

    sea_spread = models.PositiveIntegerField(blank=False, 
                                              validators=[MaxValueValidator(100),
                                                          MinValueValidator(1)],
                                              help_text="1 to 100",)


    ARID = 'AR'
    TROPICAL = 'TR'
    TEMPERATE = 'TP'
    POLAR = 'PL'
    COLD_WET = 'CD'
    DRUG = 'RX'
    EXAM = 'IX'

    RESISTANCE_CHOICES = (
        (ARID, 'Arid'),
        (TROPICAL, 'Tropical'),
        (TEMPERATE, 'Temperate'),
        (POLAR, 'Polar'),
        (COLD_WET, 'Cold and wet'),
        (DRUG, 'Drug resistance'),
        (EXAM, 'Resistance to research')
    )

    resistance = models.CharField(max_length=2,
                                  choices=RESISTANCE_CHOICES,
                                  blank=True,
                                  )
    class Meta:
        verbose_name = "Virus type"
        verbose_name_plural = "Virus types"
    
    def __unicode__(self):
        return self.agent


    def add_infected_country(self, countries_to_infect):
        if type(countries_to_infect) == list:
            for c in countries_to_infect:
                self.infected_countries.add(c)
        else:
            self.infected_countries.add(countries_to_infect)
        self.save()

    def stats_to_json(self):
        """
        Returns a string of JSON with virus stats.
        Used for starting a new game
        """
        return json.dumps({'agent': self.agent,
                           'points': self.points,
                           'shift': float(self.shift),
                           'infectivity': self.infectivity,
                           'lethality': self.lethality,
                           'resistance': self.resistance,
                           'air_spread': self.air_spread,
                           'land_spread': self.land_spread,
                           'sea_spread': self.sea_spread
                       }, sort_keys=True, indent=2)


class virus_tech_tree_node(models.Model):
    """
    links up one to one with the objects used by angular to make up the 
    virus tech tree
    """
    name = models.CharField(blank=False, max_length=512) # used as the key and also the property field
    
    display_active = models.TextField(blank=False, 
                                      help_text="HTML that is displayed in a node when it is active")

    display_inactive = models.TextField(blank=False, 
                                      help_text="HTML that is displayed in a node when it is INactive")

    parent = models.ForeignKey('self', blank=True, null=True) 
    # NOTE: will need to account for base nodes by testing if this field is emptying when
    # first creating the tech tree for each game in views

    # toolTip isnt used properly. Name is duplicated into it

    active = models.BooleanField(default=False)

    selectable = models.BooleanField(default=True, 
                                     help_text="Whether a node is selectable or just for info")

    cost = models.PositiveIntegerField(blank=False, default=1)

    requires = models.ManyToManyField('self', blank = True, related_name = 'req+', symmetrical = False)

    effect_on_infectivity = models.PositiveIntegerField(blank=False, default=0)
    effect_on_lethality = models.PositiveIntegerField(blank=False, default=0)
    effect_on_shift = models.PositiveIntegerField(blank=False, default=0)
    effect_on_land_spread = models.PositiveIntegerField(blank=False, default=0)
    effect_on_sea_spread = models.PositiveIntegerField(blank=False, default=0)
    effect_on_air_spread = models.PositiveIntegerField(blank=False, default=0)

    class Meta:
        verbose_name = "Virus tech tree node"
        verbose_name_plural = "Virus tech tree nodes"
    
    def __unicode__(self):
        return self.name

    def stats_to_dict(self):
        """
        Returns a dict with node stats, ready for use by front end
        """
        r = []
        for x in self.requires.all():
            r.append(x.name)

	if r == []:
	    r = ''

        if self.parent is None:
            parent = 0
        else:
            parent = self.parent.name

        return {self.name: 
                           {'id': self.id,
                            'property': self.name,
                            'display_inactive': self.display_inactive,
                            'display_active': self.display_active,
                            'parent': parent,
                            'toolTip': self.name,
                            'active': self.active,
                            'selectable': self.selectable,
                            'cost': self.cost,
                            'requires': r,
                            'effect_on_infectivity': self.effect_on_infectivity,
                            'effect_on_land_spread': self.effect_on_land_spread,
                            'effect_on_lethality': self.effect_on_lethality,
                            'effect_on_sea_spread': self.effect_on_sea_spread,
                            'effect_on_air_spread': self.effect_on_air_spread,
                            'effect_on_shift': self.effect_on_shift,
                            }}



class virus_tech_tree(models.Model):
    """
    Complete tech tree, linked to a single virus type
    """
    agent = models.ForeignKey(Virus_player, blank=False, 
                              help_text="Agent that this tech tree represents")

    nodes = models.ManyToManyField(virus_tech_tree_node, blank=True)

    class Meta:
        verbose_name = "Virus tech tree"
        verbose_name_plural = "Virus tech trees"

    def __unicode__(self):
        return str(self.agent.agent) + " tech tree"

    def to_dict(self):
        d = {}
        for c in self.nodes.all():
            d[c.name] = c.stats_to_dict()[c.name]
	    for node in d[c.name]['requires']:
                n = virus_tech_tree_node.objects.get(name = node)
		if n not in self.nodes.all():  # if required node is not in tree
		    self.nodes.add(n)  #  add it
		    self.save()
                    return "restart"    		    
        return d

    def to_json(self):
        """
        Returns a string of JSON with complete tree
        """
	while self.to_dict() == "restart":
	    tree_dict = self.to_dict()
	tree_dict = self.to_dict()
        return json.dumps(tree_dict, 
                          sort_keys=True, indent=2)
