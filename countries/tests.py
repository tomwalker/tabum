from django.test import TestCase

from countries.models import Country, Map

class TestCountries(TestCase):
    def setUp(self):
        Country.objects.create(name="China", 
                               population="1400000000", 
                               climate='TEMPERATE', healthcare="4")
        Country.objects.create(name="India", 
                               population="1300000000", 
                               climate='TROPICAL', healthcare="3")
        Country.objects.create(name="Nepal", 
                               population="10", 
                               climate='ARID', healthcare="1")

    def test_setup_data(self):
        china = Country.objects.get(name="China")
        self.assertEqual(china.population, 1400000000)
        self.assertEqual(china.climate, 'TEMPERATE')
        self.assertEqual(china.healthcare, 4)

    def test_adding_link(self):
        china = Country.objects.get(name="China")
        india = Country.objects.get(name="India")
        china.add_link("land", india)
        self.assertIn(india, china.land_links.all())
        self.assertIn(china, india.land_links.all())

    def test_adding_many_links(self):
        china = Country.objects.get(name="China")
        india = Country.objects.get(name="India")
        nepal = Country.objects.get(name="Nepal")

        china.add_link("land", [india, nepal])
        self.assertIn(india, china.land_links.all())
        self.assertIn(china, india.land_links.all())

        self.assertIn(china, nepal.land_links.all())
        self.assertIn(nepal, china.land_links.all())

        self.assertNotIn(india, nepal.land_links.all())

    def test_air_sea_links(self):
        china = Country.objects.get(name="China")
        india = Country.objects.get(name="India")
        nepal = Country.objects.get(name="Nepal")

        china.add_link("air", [india, nepal])
        china.add_link("sea", india)

        self.assertIn(india, china.air_links.all())
        self.assertIn(nepal, china.air_links.all())
        self.assertIn(india, china.sea_links.all())

    def test_map(self):
        world_map = Map.objects.create(name="earth")
        china = Country.objects.get(name="China")
        india = Country.objects.get(name="India")
        nepal = Country.objects.get(name="Nepal")

        world_map.add_country([india, nepal])
        world_map.add_country(china)

        self.assertIn(india, world_map.countries.all())
        self.assertIn(nepal, world_map.countries.all())
        self.assertIn(china, world_map.countries.all())

    def test_map_to_json(self):
        world_map = Map.objects.create(name="earth")
        china = Country.objects.get(name="China")
        india = Country.objects.get(name="India")
        nepal = Country.objects.get(name="Nepal")

        china.add_link("land", [india, nepal])
        china.add_link("air", [india, nepal])
        china.add_link("sea", india)

        world_map.add_country([india, nepal, china])

        self.assertIn('"healthcare": 4,', world_map.to_json())
        self.assertIn('"research_teams": 0,', world_map.to_json())
        self.assertIn('"climate": "TEMPERATE"', world_map.to_json())











