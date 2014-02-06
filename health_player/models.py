import json
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Health_player(models.Model):
    name = models.CharField(blank=False, max_length=256)

    points = models.IntegerField(blank=False, 
                                 validators=[MaxValueValidator(100), 
                                             MinValueValidator(0)], 
                                 help_text="0 to 100")

    field_researchers = models.IntegerField(blank=False, 
                                            validators=[MaxValueValidator(20), 
                                                        MinValueValidator(0)], 
                                            help_text="0 to 20", 
                                            default=1)
    
    control_team = models.IntegerField(blank=False,
                                       validators=[MaxValueValidator(5), 
                                                   MinValueValidator(0)], 
                                       help_text="0 to 5", 
                                       default=0)

    virus_understanding = models.IntegerField(blank=False,
                                              validators=[MaxValueValidator(100), 
                                                          MinValueValidator(0)], 
                                              help_text="0 to 100", 
                                              default=0)

    cure_research = models.IntegerField(blank=False, 
                                        validators=[MaxValueValidator(100), 
                                                    MinValueValidator(0)], 
                                        help_text="0 to 100", 
                                        default=0)

    public_awareness = models.IntegerField(blank=False,
                                           validators=[MaxValueValidator(100), 
                                                       MinValueValidator(0)], 
                                           help_text="0 to 100", 
                                           default=0)

    disease_control = models.IntegerField(blank=False, 
                                          validators=[MaxValueValidator(100), 
                                                      MinValueValidator(0)], 
                                          help_text="0 to 100", 
                                          default=0)

    class Meta:
        verbose_name = "Healthcare type"
        verbose_name_plural = "Healthcare types"
    
    def __unicode__(self):
        return self.name


    def stats_to_json(self):
        """
        Returns a string of JSON with health stats.
        Used for starting a new game
        """
        return json.dumps({'name': self.name,
                           'points': self.points,
                           'field_researchers': self.field_researchers,
                           'control_team': self.control_team,
                           'virus_understanding': self.virus_understanding,
                           'cure_research': self.cure_research,
                           'public_awareness': self.public_awareness,
                           'disease_control': self.disease_control
                       }, sort_keys=True, indent=2)


class health_tech_tree_node(models.Model):
    """
    links up one to one with the objects used by angular to make up the 
    health tech tree
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

    effect_on_field_researchers = models.PositiveIntegerField(blank=False, default=0)
    effect_on_control_teams = models.PositiveIntegerField(blank=False, default=0)
    effect_on_virus_understanding = models.PositiveIntegerField(blank=False, default=0)
    effect_on_cure_research = models.PositiveIntegerField(blank=False, default=0)
    effect_on_public_awareness = models.PositiveIntegerField(blank=False, default=0)
    effect_on_disease_control = models.PositiveIntegerField(blank=False, default=0)

    class Meta:
        verbose_name = "Health tech tree node"
        verbose_name_plural = "Health tech tree nodes"
    
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
                            'effect_on_field_researchers': self.effect_on_field_researchers,
                            'effect_on_control_teams': self.effect_on_control_teams,
                            'effect_on_virus_understanding': self.effect_on_virus_understanding,
                            'effect_on_cure_research': self.effect_on_cure_research,
                            'effect_on_public_awareness': self.effect_on_public_awareness,
                            'effect_on_disease_control': self.effect_on_disease_control,
                            }}

class health_tech_tree(models.Model):
    """
    Complete tech tree, linked to a single health type
    """
    agency = models.ForeignKey(Health_player, blank=False, 
                              help_text="Health organisation that this tech tree represents")

    nodes = models.ManyToManyField(health_tech_tree_node, blank=True)

    class Meta:
        verbose_name = "Health player tech tree"
        verbose_name_plural = "Health player tech trees"

    def __unicode__(self):
        return str(self.agency.name) + " tech tree"

    def to_dict(self):
        d = {}
        for c in self.nodes.all():
            d[c.name] = c.stats_to_dict()[c.name]
	    for node in d[c.name]['requires']:
                n = health_tech_tree_node.objects.get(name = node)
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
