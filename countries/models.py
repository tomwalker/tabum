import json
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator



class Country(models.Model):
    name = models.CharField(blank=False, max_length=256)

    population = models.PositiveIntegerField(blank=False)

    ARID = 'AR'
    TROPICAL = 'TR'
    TEMPERATE = 'TP'
    POLAR = 'PL'
    COLD_WET = 'CD'

    CLIMATE_CHOICES = (
        (ARID, 'Arid'),
        (TROPICAL, 'Tropical'),
        (TEMPERATE, 'Temperate'),
        (POLAR, 'Polar'),
        (COLD_WET, 'Cold and wet')
    )

    climate = models.CharField(max_length=2,
                                choices=CLIMATE_CHOICES,
                                default=TEMPERATE)

    healthcare = models.IntegerField(blank=False, 
                                     default=5, 
                                     validators=[MaxValueValidator(10), 
                                                 MinValueValidator(1)], 
                                     help_text="1 is low, 10 is high")

    land_links = models.ManyToManyField('self', blank=True,)
    air_links = models.ManyToManyField('self', blank=True,)
    sea_links = models.ManyToManyField('self', blank=True,)

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
    
    def __unicode__(self):
        return self.name

    def add_link(self, connection, countries_to_link):
        current_links = getattr(self, str(connection + "_links"))
        if type(countries_to_link) == list:
            for c in countries_to_link:
                current_links.add(c)
        else:
            current_links.add(countries_to_link)
        self.save()

    def stats_to_dict(self):
        """
        Returns a string of JSON with country stats.
        Used by Map class for starting a new game.
        """
        l = []
        for x in self.land_links.all():
            l.append(x.name)

        a = []
        for y in self.air_links.all():
            a.append(y.name)

        s = []
        for z in self.sea_links.all():
            s.append(z.name)

        return {self.name: 
                           {'population': {
                               'healthy': self.population,
                               'infected': 0,
                               'dead': 0},
                            "climate": self.climate,
                            "healthcare": self.healthcare,
                            "land_links": l,
                            "air_links": a,
                            "sea_links": s,
                            "control_teams": 0,
                            'research_teams': 0,
                            'cure_teams': 0,
                            }}

    def to_json(self):
        x = self.stats_to_dict()
        return json.dumps(x)

class Map(models.Model):
    """
    Map stores the countries that make up a map.
    
    """
    name = models.CharField(blank=False, max_length=256)
    countries = models.ManyToManyField(Country, blank=True, )

    class Meta:
        verbose_name = "Map"
        verbose_name_plural = "Maps"
    
    def __unicode__(self):
        return self.name

    def add_country(self, countries_to_add):
        if type(countries_to_add) == list:
            for c in countries_to_add:
                self.countries.add(c)
        else:
            self.countries.add(countries_to_add)
        self.save()

    def to_dict(self):
        d = {}
        for c in self.countries.all():
            d[c.name] = c.stats_to_dict()[c.name]
        return d

    def to_json(self):
        """
        Returns a string of JSON with country stats.
        Used for starting a new game
        """
        # return json.dumps({'countries': self.to_dict()}, 
        #                   sort_keys=True, indent=2)
        return json.dumps(self.to_dict(), 
                          sort_keys=True, indent=2)
