from django import template
from django.utils.safestring import mark_safe

from sharinator.equipment.helpers import image
from sharinator.equipment.models import Photograph

register = template.Library()

@register.simple_tag
def render_image(p: Photograph, *args, **kwargs):
    link: bool = True
    width: int = 800
    height: int = 600
    if "link" in kwargs:
        link = bool(kwargs["link"])
    if "width" in kwargs:
        width = int(kwargs["width"])
    if "height" in kwargs:
        height = int(kwargs["height"])
    custom_style: str = None
    if "style" in kwargs:
        custom_style = str(kwargs["style"])
    a = image.render_as_large_image(p, link, width, height, custom_style=custom_style)
    for pp in args:
        a += image.render_as_large_image(pp, link, width, height, custom_style=custom_style)
    return mark_safe(a)

@register.simple_tag
def render_icon(p: Photograph, *args, **kwargs):
    width: int = 32
    height: int = 32
    if "width" in kwargs:
        width = int(kwargs["width"])
    if "height" in kwargs:
        height = int(kwargs["height"])
    a = image.render_as_icon(p, width, height)
    for pp in args:
        image.render_as_icon(pp, width, height)
    return mark_safe(a)

