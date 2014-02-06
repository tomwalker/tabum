from django.core.exceptions import ValidationError
import json

def validate_positive(value):
    if value < 0:
        raise ValidationError(u'%s is not a postive number' % value)

def validate_json(value):
    try:
        json.loads(value)
    except ValueError:
        raise ValidationError(u'Json is not correctly formatted')
