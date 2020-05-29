from django.conf import settings
from django.urls import reverse
from django.utils.html import format_html, escape, mark_safe

from sharinator.equipment.models import Photograph

def render_as_large_image(p: Photograph, link=True, target_width=600, target_height=500):
    if p is None:
        return format_html('<img src="{}" alt="{}"/>', \
                settings.STATIC_URL + "/icons/missing-picture.svg", 
                "Missing image. Sorry.")
    img_url: str = p.image.url
    descr: str = p.title
    style_str: str = ""
    if p.image.width > target_width or p.image.height > target_height:
        w: int = p.image.width
        h: int = p.image.height
        while w > target_width or h > target_height:
            w /= 2
            h /= 2
        style_str = 'style="width:{}px;height:{}px;"'.format(escape(w), escape(h))
    if link:
        detail_page_url: str = reverse("image_detail_page", args=[p.id])
        return format_html('<a href="{}"><img src="{}" alt="{}" {} /></a>', \
                detail_page_url, img_url, descr, mark_safe(style_str))
    else:
        return format_html('<img src="{}" alt="{}" {} />', img_url, descr, mark_safe(style_str))

def render_as_icon(p: Photograph):
    if p is None:
        return format_html('<img src="{}", alt="{}", style="width:32px;height:32px;" />',
                settings.STATIC_URL + "/icons/missing-picture.svg", "Missing icon. Sorry.")
    img_url: str = p.image.url
    descr: str = p.title
    return format_html('<img src="{}" alt="{}" style="width:32px;height:32px;" />', img_url, descr)
