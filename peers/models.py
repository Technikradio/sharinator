import datetime

from django.contrib.auth.models import User
from django.db import models

from sharinator.equipment.models import Photograph

class PeerGroup(models.Model):
    name = models.CharField(max_length=100)
    notes = models.TextField(blank=True, help_text="Further description of the group. Markdown supported.")
    created_at = models.DateField(editable=False, default=datetime.date.today, help_text="Date of creation")
    members = models.ManyToManyField(User)
    admins = models.ManyToManyField(User)
    icon = models.ForeignKey(Photograph, null=True)
    visible_to_strangers = models.BooleanField(default=False, help_text="If true one can apply for becomming a member")
    applications = models.ManyToManyField(User, through="GroupApplication")

    class Meta:
        ordering = ["name", "created_at"]

class GroupApplication(models.Model):
    applicant = models.ForeignKey(User, null=False)
    application_for = models.ForeignKey(PeerGroup, null=False)
    approved_by = models.ManyToManyField(User, help_text="Once all admins of a group approved the application, "\
            "the last approving admin can fulfill it.")
    applied_at = models.DateField(editable=False, default=datetime.date.today, help_text="Date of application")
    declined = models.BooleanField(default=False, help_text="A declined application won't be deleted."\
            " Once an application was declined the user can't reapply. A declined application can be reenabled.")
    declined_by = models.ForeignKey(User, null=True, default=None)

    class Meta:
        ordering = ["declined", "applied_at"]

