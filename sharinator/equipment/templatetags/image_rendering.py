from django import template

from sharinator.equipment.helpers import image
from sharinator.equipment.models import Photograph

register = template.Library()

@register.simple_tag
def render_image(p: Photograph, link=True, target_width=600, target_height=500):
    return image.render_as_large_image(p, link, target_width, target_height)

@register.simple_tag
def render_icon(p: Photograph):
    return image.render_as_icon(p)

