import datetime
import time

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from sharinator.equipment.models import Item
from sharinator.shares.models import Lending

class LendingCreationTestCase(TestCase):

    def setUp(self):
        u: User = User()
        u.username = "testme"
        u.save()
        Item.objects.create(name="item to lend", owner=u)
        Item.objects.create(name="Another Item", owner=u)

    def test_lending_times(self):
        u: User = User.objects.get(username="testme")
        i: Item = Item.objects.get(name="item to lend")
        now = int(time.mktime(datetime.datetime.now().timetuple()))
        l: Lending = Lending()
        l.lending_user = u
        l.item_to_lend = i

        # Test start date in past
        l.start_of_lending = datetime.datetime.fromtimestamp(now - 3600*25)
        l.end_of_lending = datetime.datetime.fromtimestamp(now + 3600*25)
        self.assertRaises(ValidationError, l.save)

        # Test end date in past
        l.start_of_lending = datetime.datetime.fromtimestamp(now + 3600*25)
        l.end_of_lending = datetime.datetime.fromtimestamp(now - 3600*25)
        self.assertRaises(ValidationError, l.save)

        # Test end date prior to start date
        l.start_of_lending = datetime.datetime.fromtimestamp(now + 3600*49)
        l.end_of_lending = datetime.datetime.fromtimestamp(now + 3600*25)
        self.assertRaises(ValidationError, l.save)

        # Test successfull save
        l.start_of_lending = datetime.datetime.fromtimestamp(now + 3600*25)
        l.end_of_lending = datetime.datetime.fromtimestamp(now + 3600*49)
        l.save()

    def test_lending_overlaps(self):
        u: User = User.objects.get(username="testme")
        i: Item = Item.objects.get(name="item to lend")
        now = int(time.mktime(datetime.datetime.now().timetuple()))
        l: Lending = Lending()
        l.lending_user = u
        l.item_to_lend = i
        l.start_of_lending = datetime.datetime.fromtimestamp(now + 3600*25)
        l.end_of_lending = datetime.datetime.fromtimestamp(now + 3600*49)
        l.save()

        # Test sucessfull additional lending
        l = Lending()
        l.lending_user = u
        l.item_to_lend = i
        l.start_of_lending = datetime.datetime.fromtimestamp(now + 3600*121)
        l.end_of_lending = datetime.datetime.fromtimestamp(now + 3600*169)
        l.save()

        # Test successfull overlapping different item
        i2 = Item.objects.get(name="Another Item")
        l = Lending()
        l.lending_user = u
        l.item_to_lend = i2
        l.start_of_lending = datetime.datetime.fromtimestamp(now + 3600*121)
        l.end_of_lending = datetime.datetime.fromtimestamp(now + 3600*145)
        l.save()

        # Test failing overlapping same item
        l = Lending()
        l.lending_user = u
        l.item_to_lend = i
        l.start_of_lending = datetime.datetime.fromtimestamp(now + 3600*145)
        l.end_of_lending = datetime.datetime.fromtimestamp(now + 3600*193)
        self.assertRaises(ValidationError, l.save)

