from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from sharinator.equipment.models import Item

class ItemCreationTestCase(TestCase):

    def setUp(self):
        u: User = User()
        u.username = "testme"
        u.save()
        Item.objects.create(name="legid container",
                notes=" * Test markdown capability",
                owner=u,
                is_container=True)

    def test_container_saving_errors(self):
        u: User = User.objects.get(username="testme")
        ic: Item = Item()
        ic.name = "not a container"
        ic.owner = u
        ic.save()
        i: Item = Item()
        i.name = "Should fail"
        i.parent_container = ic
        i.owner = u
        self.assertRaises(ValidationError, i.save)
        ic.is_container = True
        ic.save()
        i.save()

    def test_markdown_cache(self):
        i = Item.objects.get(name="legid container")
        self.assertTrue("<li>" in i.notes_cache)
        self.assertTrue("</li>" in i.notes_cache)


