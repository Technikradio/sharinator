import datetime

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import TestCase
from django.template import Context, Template

from sharinator.equipment.models import Item
from sharinator.shares.models import Lending
from sharinator.shares.views.lend_views import MyLendsView


class MyLendingsViewTestCase(TestCase):
    def setUp(self):
        u: User = User.objects.create_user(username="lendingtestuser", password="1234")
        u.set_password("1234")
        u.save()
        for i in range(10):
            item = Item.objects.create(name="test item " + str(i), owner=u)
            Lending.objects.create(
                lending_user=u,
                item_to_lend=item,
                start_of_lending=datetime.date.today() + datetime.timedelta(days=1),
                end_of_lending=datetime.date.today() + datetime.timedelta(days=2),
            )
        item = Item.objects.create(name="The other test item", owner=u)
        Lending.objects.create(
            lending_user=u,
            item_to_lend=item,
            start_of_lending=datetime.date.today() + datetime.timedelta(days=5),
            end_of_lending=datetime.date.today() + datetime.timedelta(days=6),
        )

    def test_context_generation(self):
        l = self.client.login(username="lendingtestuser", password="1234")
        response = self.client.get(reverse("mylends"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["more_future_lendings"])
        self.assertEqual(len(response.context["future_lend_groups"]), 2)
        self.assertEqual(len(response.context["future_lend_groups"][0]), 10)
        self.assertEqual(len(response.context["future_lend_groups"][1]), 1)
        self.assertEqual(
            response.context["future_lend_groups"][1][0].item_to_lend.name,
            "The other test item",
        )

    def test_correct_user_data(self):
        pass  # TODO implement using self.client.get
