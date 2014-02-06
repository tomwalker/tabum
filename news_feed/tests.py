from django.test import TestCase

from news_feed.models import NewsItem

class TestNewsModel(TestCase):
    def setUp(self):
        NewsItem.objects.create(story = "This is a",
                                story_type = 'N')
        NewsItem.objects.create(story = "True story",
                                story_type = 'T')
        NewsItem.objects.create(story = "False story",
                                story_type = 'F')

    def test_setup(self):
        n1 = NewsItem.objects.get(id = 1)
        n2 = NewsItem.objects.filter(story_type = 'T')
        n3 = NewsItem.objects.filter(story_type = 'F').count()
        self.assertEqual(n1.story, "This is a")
        self.assertEqual(n2.count(), 1)
        self.assertEqual(n3, 1)










