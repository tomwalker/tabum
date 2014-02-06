from django.test import TestCase

from health_player.models import Health_player, health_tech_tree_node, health_tech_tree

from core.factories import HealthTechNodeFactory, HealthTechTreeFactory, HealthTypeFactory

class TestHealthPlayers(TestCase):
    def setUp(self):
        Health_player.objects.create(name="WHO", 
                                     points=10, 
                                     field_researchers=1, 
                                     control_team=1, 
                                     virus_understanding=10, 
                                     cure_research=20, 
                                     public_awareness=30, 
                                     disease_control=40)
    
    def test_setup_date(self):
        who = Health_player.objects.get(name="WHO")
        self.assertEqual(who.points, 10)
        self.assertEqual(who.field_researchers, 1)
        self.assertEqual(who.control_team, 1)
        self.assertEqual(who.virus_understanding, 10)
        self.assertEqual(who.cure_research, 20)
        self.assertEqual(who.public_awareness, 30)
        self.assertEqual(who.disease_control, 40)

    def test_stats_to_json(self):
        who = Health_player.objects.get(name="WHO")
        self.assertIn('"name": "WHO"', who.stats_to_json())

class TestHealthTechTree(TestCase):
    def setUp(self):
        who = HealthTypeFactory()
        research_node1 = HealthTechNodeFactory()
        research_node2 = HealthTechNodeFactory(name = 'more research')
        health_tree = HealthTechTreeFactory(agency = who,
                                            nodes = (research_node1,
                                                     research_node2))

    def test_TT_methods(self):
        n1 = health_tech_tree_node.objects.get(name = 'cure')
        who = Health_player.objects.get(name = 'WHO')
        tree = health_tech_tree.objects.get(agency = who)
        
        self.assertEqual(n1.active, False)
        self.assertEqual(n1.effect_on_cure_research, 0)
        self.assertEqual(who.name, tree.agency.name)
        self.assertEqual(tree.nodes.count(), 2)

        tree_dict = tree.to_dict()
        self.assertEqual(tree_dict['cure']['active'], False)
        self.assertEqual(tree_dict['more research']['effect_on_public_awareness'],
                         0)

        tree_json = tree.to_json()
        self.assertIn('"cost": 10', tree_json)
        self.assertIn('"cure"', tree_json)
        self.assertIn('"effect_on_control_teams"', tree_json)





