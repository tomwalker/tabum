from django.test import TestCase

from virus_player.models import Virus_player, virus_tech_tree, virus_tech_tree_node
from countries.models import Country

from core.factories import VirusTechNodeFactory, VirusTechTreeFactory, VirusTypeFactory

class TestVirusPlayer(TestCase):
    def setUp(self):
        Virus_player.objects.create(agent="HIV", 
                                    points=11, 
                                    shift=4, 
                                    infectivity=4, 
                                    lethality=2,
                                    resistance="TR",
                                    air_spread=3,
                                    land_spread=6,
                                    sea_spread=1, )
        

    def test_setup_data(self):
        hiv = Virus_player.objects.get(agent="HIV")
        self.assertEqual(hiv.points, 11)
        self.assertEqual(float(hiv.shift), 4)
        self.assertEqual(hiv.infectivity, 4)
        self.assertEqual(hiv.lethality, 2)
        self.assertEqual(hiv.resistance, "TR")
        self.assertEqual(hiv.air_spread, 3)
        self.assertEqual(hiv.land_spread, 6)
        self.assertEqual(hiv.sea_spread, 1)

    # The following tests have been removed as these models are not used to 
    # store the state of the game; they are only used to initialise the game

    # def test_add_infected_country(self):
    #     hiv = Virus_player.objects.get(agent="HIV")
    #     Country.objects.create(name="China", 
    #                            population="1400000000", 
    #                            climate='TEMPERATE', healthcare="4")
    #     china = Country.objects.get(name="China")
    #     hiv.add_infected_country(china)
    #     self.assertIn(china, hiv.infected_countries.all())

    # def test_add_infected_countries(self):
    #     hiv = Virus_player.objects.get(agent="HIV")
    #     Country.objects.create(name="China", 
    #                            population="1400000000", 
    #                            climate='TEMPERATE', healthcare="4")
    #     Country.objects.create(name="India", 
    #                            population="1300000000", 
    #                            climate='TROPICAL', healthcare="3")
    #     Country.objects.create(name="Nepal", 
    #                            population="10", 
    #                            climate='ARID', healthcare="1")
    #     china = Country.objects.get(name="China")
    #     india = Country.objects.get(name="India")
    #     nepal = Country.objects.get(name="Nepal")

    #     hiv.add_infected_country([china, india, nepal])
    #     self.assertIn(china, hiv.infected_countries.all())
    #     self.assertIn(india, hiv.infected_countries.all())
    #     self.assertIn(nepal, hiv.infected_countries.all())

    def test_stats_to_json(self):
        hiv = Virus_player.objects.get(agent="HIV")
        Country.objects.create(name="China", 
                               population="1400000000", 
                               climate='TEMPERATE', healthcare="4")
        Country.objects.create(name="India", 
                               population="1300000000", 
                               climate='TROPICAL', healthcare="3")

        self.assertIn('"agent": "HIV"', hiv.stats_to_json())

        
class TestVirusTechTree(TestCase):
    def setUp(self):
        fungus = VirusTypeFactory(agent = 'fungus')        
        parent_node = VirusTechNodeFactory(name = 'parent')
        anaemia = VirusTechNodeFactory()
        fever = VirusTechNodeFactory(name = 'fever')
        tree = VirusTechTreeFactory(agent = fungus, nodes = (anaemia, fever))

    def test_TT_methods(self):
        anaemia = virus_tech_tree_node.objects.get(name = 'anaemia')
        fungus = Virus_player.objects.get(agent = 'fungus')        
        tree = virus_tech_tree.objects.get(agent = fungus)
        
        self.assertEqual(anaemia.active, False)
        self.assertEqual(anaemia.effect_on_air_spread, 0)
        self.assertEqual(fungus.agent, tree.agent.agent)
        self.assertEqual(tree.nodes.count(), 2)

        tree_dict = tree.to_dict()
        self.assertEqual(tree_dict['fever']['active'], False)
        self.assertEqual(tree_dict['anaemia']['toolTip'], 'anaemia')

        tree_json = tree.to_json()
        self.assertIn('"cost": 10', tree_json)
        self.assertIn('"fever"', tree_json)
        self.assertIn('"effect_on_shift"', tree_json)
