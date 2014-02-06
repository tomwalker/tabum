import json, random

from celery import task

from engine.begin import normal_turn

from choices.models import ChoiceQuestion

from news_feed.models import NewsItem

@task(CELERY_IGNORE_RESULT = True, )
def add(x, y):
    return x + y

def create_news_items(output):
    news_items = []
    exclude_list = []

    for x in range(10):     # 10 random nonsense news items
        nonsense_news_queryset = NewsItem.objects.filter(story_type = 'N')
        for i in exclude_list:
            nonsense_news_queryset = nonsense_news_queryset.exclude(id = i)
        news_idx = random.randint(0, nonsense_news_queryset.count() - 1)
        news_id = nonsense_news_queryset[news_idx].id
        news_items.append(NewsItem.objects.get(id = news_id).story.upper())
        exclude_list.append(int(news_id))

    false_news_queryset = NewsItem.objects.filter(story_type = 'F')
    false_idx = random.randint(0, false_news_queryset.count() - 1)
    false_id = false_news_queryset[false_idx].id
    false_story = NewsItem.objects.get(id = false_id).story.replace(
        '$COUNTRY$', random.choice(output["countries"].keys()))
    news_items.append(false_story.upper()) # 1 false story

    if len(output["detected_infection"]) > 0:
        true_news_queryset = NewsItem.objects.filter(story_type = 'T')
        true_idx = random.randint(0, true_news_queryset.count() - 1)
        true_id = true_news_queryset[true_idx].id
        true_story = NewsItem.objects.get(id = true_id).story.replace(
            '$COUNTRY$', random.choice(output["detected_infection"]))
        news_items.append(true_story.upper()) # 1 true story

    return news_items
            
@task(CELERY_IGNORE_RESULT = True, )
def normal_turn_process_store(virus_change, health_change, c, change, choices_blank, first_turn, 
                              game_session, next_to_play, virus_tt, health_tt):

    if 'detected_infection' in json.loads(game_session.turn_data):
        detected_infection = json.loads(game_session.turn_data)['detected_infection']
    else:
        detected_infection = []
        
    output = normal_turn(virus_change, health_change, c, change, choices_blank, detected_infection, first_turn)

    if next_to_play == 'V' and output["health_win"] == True:
        # health win
        choice = {
            'story': 'The World Health Organisation contained the infection',
            'question': 'The infection has been eradicated and no one on Earth is infected.',
            'choices': ['1', '0'],
            'choice_values': ['1', '0']
            }
        output["game_ended"] = True
        game_session.finish_game('H')

    elif next_to_play == 'H' and output["virus_win"] == True:
        # virus win
        choice = {
            'story': 'The infection has eradicated all human life',
            'question': 'Everyone is dead. The WHO has failed its duty to protect humanity.',
            'choices': ['1', '0'],
            'choice_values': ['1', '0']
            }
        output["game_ended"] = True
        game_session.finish_game('V')

    else:
        # add the question for next turn
        v_turn_question_queryset = ChoiceQuestion.objects.filter(question_for = next_to_play)
        random_idx = random.randint(0, v_turn_question_queryset.count() - 1)
        random_q_id = v_turn_question_queryset[random_idx].id
        choice = ChoiceQuestion.objects.get(id = random_q_id).to_dict()
        

    output["turn_question"] = choice

    # add the tech trees
    output["virus_tech_tree"] = virus_tt
    output["health_tech_tree"] = health_tt

    # add the news ticker items if health
    if next_to_play == 'H' and game_session.game_over != True:

        output["news"] = create_news_items(output)

    output["first_turn"] = False

    game_session.set_turn_data(json.dumps(output), next_to_play)






