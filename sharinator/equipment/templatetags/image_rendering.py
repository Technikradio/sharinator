from django import template

from sharinator.equipment.helpers import image
from sharinator.equipment.models import Photograph

register = template.Library()

@register.simple_tag
def render_image(p: Photograph, link=True, width=600, height=500):
    return image.render_as_large_image(p, link, width, height)

@register.simple_tag
def render_icon(p: Photograph, width=32, height=32):
    return image.render_as_icon(p, width, height)

