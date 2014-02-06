from django.test import TestCase

from choices.models import ChoiceQuestion
from core.factories import ChoiceQuestionFactory

class TestChoicesModels(TestCase):
    def setUp(self):
        choice1 = ChoiceQuestionFactory()

    def test_setup_data(self):
        c1 = ChoiceQuestion.objects.get(story='Once upon a time')
        self.assertEqual(c1.question_for, 'V')
        self.assertEqual(c1.choice_2_value, 2)

    def test_to_dict(self):
        c1 = ChoiceQuestion.objects.get(story='Once upon a time')
        out = c1.to_dict()
        self.assertEqual(out['story'], 'Once upon a time')
        self.assertEqual(out['choice_values'], [1, 2])

    def test_to_json(self):
        c1 = ChoiceQuestion.objects.get(story='Once upon a time')
        out = c1.to_json()
        self.assertIn('Once upon a time', out)
