from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def true_news(context, story, country):
    changed_story = story.replace('$COUNTRY$', country)
    return changed_story










