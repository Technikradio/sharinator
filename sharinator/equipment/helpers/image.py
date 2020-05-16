from django.urls import reverse

from sharinator.equipment.models import Photograph

def render_as_large_image(p: Photograph, link=True, target_width=600, target_height=500):
    img_url: str = p.image.url
    descr: str = p.title
    style_str: str = ""
    if p.image.width > target_width or p.image.height > target_height:
        w: int = p.image.width
        h: int = p.image.height
        while w > target_width or h > target_height:
            w /= 2
            h /= 2
        style_str = 'style="width:{}px;height:{}px;"'.format(w, h)
    if link:
        detail_page_url: str = reverse("image_detail_page", args=[p.id])
        return '<a href="{}"><img src="{}" alt="{}" {} /></a>'.format( \
                detail_page_url, img_url, descr, style_str)
    else:
        return '<img src="{}" alt="{}" {} />'.format(img_url, descr, style_str)

def render_as_icon(p: Photograph):
    img_url: str = p.image.url
    descr: str = p.title
    return '<img src="{}" alt="{}" style="width:32px;height:32px;" />'.format(img_url, descr)
