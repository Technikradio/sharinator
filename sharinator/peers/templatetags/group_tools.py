from django import template
from django.contrib.auth.models import User

from sharinator.peers.models import PeerGroup

register = template.Library()


@register.filter
def user_is_admin(value: PeerGroup, u: User) -> bool:
    if not u:
        return False
    if type(u) is not User:
        return False
    if type(value) is not PeerGroup:
        return False
    return (
        u.is_superuser
        or u.is_staff
        or (value.admins.all().filter(username=u.username).exists())
    )
