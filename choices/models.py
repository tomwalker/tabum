import json
from django.db import models

class ChoiceQuestion(models.Model):

    PLAYER_CHOICES = ( ('V', 'Virus player'), ('H', 'Healthy player'))

    question_for = models.CharField(max_length=1, choices=PLAYER_CHOICES, default='V')

    story = models.TextField(editable=True, max_length=1500, help_text="HTML allowed")
    
    question = models.TextField(max_length=500, help_text="HTML allowed")
    
    choice_1 = models.CharField(max_length = 128)
    choice_2 = models.CharField(max_length = 128)
    
    choice_1_value = models.PositiveSmallIntegerField(default=0, 
                                                      help_text = "Refers to Buckets engine")
    choice_2_value = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        verbose_name = "Start of turn question"
        verbose_name_plural = verbose_name + "s"
    
    def __unicode__(self):
        return self.question

    def to_dict(self):
        return {'story': self.story,
                'question': self.question,
                'choices': [self.choice_1, self.choice_2],
                'choice_values': [self.choice_1_value, self.choice_2_value]
        }

    def to_json(self):
        """
        Returns a string of JSON
        """
        return json.dumps({"story": self.story,
                           "question": self.question,
                           "choices": [self.choice_1, self.choice_2],
                           "choice_values": [self.choice_1_value, self.choice_2_value]
                           }, 
                           sort_keys=True, indent=2)
