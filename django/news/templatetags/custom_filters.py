from django import template
from news.models import BanWords
import re
register = template.Library()


@register.filter(name='cansor')
def multiply(value):
    obsceneWords = str(BanWords.objects.get(pk=1).wordsList).split(', ')
    for word in obsceneWords:
        #value = value.replace(word, '*'*len(word))
        value = re.sub(pattern=word, repl='*'*len(word),
                       string=value, flags=re.IGNORECASE)

    return value
