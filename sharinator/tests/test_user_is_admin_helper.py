import datetime
import time

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from sharinator.peers.models import PeerGroup
from sharinator.peers.templatetags.group_tools import user_is_admin


class UserIsAdminHelperTestCase(TestCase):
    def setUp(self):
        u: User = User()
        u.username = "testme"
        u.save()
        PeerGroup.objects.create(name="testgroup")

    def test_user_is_admin(self):
        u: User = User.objects.get(username="testme")
        g: PeerGroup = PeerGroup.objects.get(name="testgroup")
        self.assertFalse(user_is_admin(g, u))
        self.assertFalse(user_is_admin(g, None))
        self.assertFalse(user_is_admin("Not a group", u))
        self.assertFalse(user_is_admin(g, "Not a user"))
        g.admins.add(u)
        g.save()
        self.assertTrue(user_is_admin(g, u))
