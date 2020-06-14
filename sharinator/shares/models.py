import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

import time

from sharinator.equipment.models import Item
from sharinator.equipment.helpers.markdown import compile_markdown

# Create your models here.
class Lending(models.Model):
    lending_user = models.ForeignKey(User, help_text="The user who is lending the equipment.",
            editable=False, on_delete=models.CASCADE)
    item_to_lend = models.ForeignKey(Item, editable=False, help_text="The item to lend",
            on_delete=models.CASCADE, related_name="lendings")
    start_of_lending = models.DateField(blank=False, null=False)
    end_of_lending = models.DateField(blank=False, null=False)
    notes = models.TextField(blank=True, help_text="Additional notes on the process (Markdown supported)")
    notes_cache = models.TextField(blank=True, help_text="Cache of the md version of the notes field (please don't edit manually)")

    class Meta:
        ordering = ["start_of_lending"]

    def save(self, *args, **kwargs):
        # I'm real sorry for the database server but I don't see a less complex solution.
        overlapping_filter = models.Q(start_of_lending__range=[self.start_of_lending, self.end_of_lending]) | \
                models.Q(end_of_lending__range=[self.start_of_lending, self.end_of_lending])
        if Lending.objects.filter(item_to_lend__id=self.item_to_lend.id).filter(overlapping_filter).exists():
            raise ValidationError("The requested item is already leanded in that time slot.")

        start_stamp: int = int(time.mktime(self.start_of_lending.timetuple()))
        end_stamp: int = int(time.mktime(self.end_of_lending.timetuple()))
        now_stamp: int = int(time.mktime(datetime.datetime.now().timetuple()))

        if (start_stamp < now_stamp) and (self.pk is None):
            raise ValidationError("The start date of a new lending may not be in the past")
        if (end_stamp < now_stamp) and (self.pk is None):
            raise ValidationError("The end date of a new lending may not be in the past")
        if end_stamp < start_stamp:
            raise ValidationError("The end of a lending may not be prior to its start.")

        self.notes_cache = compile_markdown(self.notes)
        super().save(*args, **kwargs)

