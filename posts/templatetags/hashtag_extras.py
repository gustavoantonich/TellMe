import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def link_hashtags(value):
    return mark_safe(re.sub(
        r'#(\w+)',
        r'<a href="/posts/hashtag/\1/" class="hashtag">#\1</a>',
        value
    ))
