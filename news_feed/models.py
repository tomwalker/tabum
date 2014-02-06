from django.db import models

class NewsItem(models.Model):
    story = models.TextField(blank = False,
                             help_text = "This is shown in the ticker. Use $COUNTRY$ as placeholder.",
                             unique = True)

    QUESTION_TYPE = ( ('T', 'True story'), ('F', 'False story'), ('N', 'Nonsense story') )

    story_type = models.CharField(max_length = 1, 
                                  choices = QUESTION_TYPE, 
                                  default='N')

    def __unicode__(self):
        return self.story[:50] + "....."


    class Meta:
        verbose_name = "News Item"
        










