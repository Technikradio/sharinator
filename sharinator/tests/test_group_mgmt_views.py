import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import TestCase
from django.template import Context, Template

from sharinator.peers.models import PeerGroup


class GroupManagementViewsTestCase(TestCase):
    def setUp(self):
        u: User = User.objects.create_user(username="grouptestuser")
        u.set_password("1234")
        u.save()

    def test_loginrequiredness(self):
        response = self.client.get(reverse("addgroup"), follow=False)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(
            response.url, settings.LOGIN_URL + "?next=" + reverse("addgroup")
        )
        l = self.client.login(username="grouptestuser", password="1234")
        response = self.client.get(reverse("addgroup"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"] is not None)
        self.assertTrue("visible_to_strangers" in str(response.context["form"]))
        self.assertFalse(
            PeerGroup.objects.all().filter(name="RandomTestGroup").exists()
        )
        response = self.client.post(
            reverse("addgroup"),
            {
                "visible_to_strangers": True,
                "name": "RandomTestGroup",
                "notes": "Some Markdown",
            },
        )
        self.assertTrue(PeerGroup.objects.all().filter(name="RandomTestGroup").exists())
        group: PeerGroup = PeerGroup.objects.get(name="RandomTestGroup")
        self.assertEquals(group.name, "RandomTestGroup")
        self.assertTrue(group.visible_to_strangers)
        self.assertEquals(group.notes, "Some Markdown")
        self.assertTrue("Some Markdown" in group.notes_cache)
        self.assertEquals(group.members.count(), 1)
        u: User = User.objects.get(username="grouptestuser")
        self.assertEquals(group.members.all()[0], u)
        self.assertEquals(group.admins.count(), 1)
        self.assertEquals(group.admins.all()[0], u)
