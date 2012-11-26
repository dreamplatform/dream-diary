
#coding=utf-8

from django import template
from dreamdiary.settings import COLORS
from dreamdiary.models import Color

register = template.Library()

@register.simple_tag
def hierarchy_item_coord(data, task_id):
    if not data:
        return ''
    for d in data:
      if 'type' in d and d['type'] == 'item':
        if 'id' in d and d['id'] == str(task_id):
          if 'x' in d and 'y' in d:
            return '%s_%s' % (d['x'], d['y'])
    return ''

@register.simple_tag
def percentage_for_user(network, user):
    return network.user_percentage(user)

@register.filter
def answers_for_user(answers, user):
    return answers.filter(work__user=user)

@register.simple_tag
def render_colorpicker(user):
    """Renders colorpicker template populated with
    possible color titles that user haves
    """
    user_colors = user.colors.all()
    colors = []
    for color in COLORS:
        rgb = ""
        title = ""
        try:
            match_color = user_colors.get(color=color)
            rgb = match_color.color
            title = match_color.title
        except Color.DoesNotExist:
            rgb = color
        item = dict()
        item['color'] = rgb
        item['title'] = title
        colors.append(item)
    return template.loader.render_to_string('dreamdiary/snippets/colorselector.html',\
            { 'colors' : colors})

