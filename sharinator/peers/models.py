import datetime

from django.contrib.auth.models import User
from django.db import models

from sharinator.equipment.helpers.markdown import compile_markdown
from sharinator.equipment.models import Photograph

class PeerGroup(models.Model):
    name = models.CharField(max_length=100)
    notes = models.TextField(blank=True, help_text="Further description of the group. Markdown supported.")
    notes_cache = models.TextField(blank=True, help_text="md cache of the notes field")
    created_at = models.DateField(editable=False, default=datetime.date.today, help_text="Date of creation")
    members = models.ManyToManyField(User, related_name="member_of_peergroups")
    admins = models.ManyToManyField(User, related_name="admin_of_peergroups")
    icon = models.ForeignKey(Photograph, null=True, on_delete=models.SET_NULL)
    visible_to_strangers = models.BooleanField(default=False, help_text="If true one can apply for becomming a member")
    applications = models.ManyToManyField(User, through="GroupApplication", through_fields=("application_for", "applicant"))

    class Meta:
        ordering = ["name", "created_at"]

    def save(self, *args, **kwargs):
        self.notes_cache = compile_markdown(self.notes)
        super().save(*args, **kwargs)

class GroupApplication(models.Model):
    applicant = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    application_for = models.ForeignKey(PeerGroup, null=False, on_delete=models.CASCADE)
    approved_by = models.ManyToManyField(User, help_text="Once all admins of a group approved the application, "\
            "the last approving admin can fulfill it.", related_name="+")
    applied_at = models.DateField(editable=False, default=datetime.date.today, help_text="Date of application")
    declined = models.BooleanField(default=False, help_text="A declined application won't be deleted."\
            " Once an application was declined the user can't reapply. A declined application can be reenabled.")
    declined_by = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL, related_name="+")
    notes = models.TextField(blank=True, help_text="optional markdown notes on the application")
    notes_cache = models.TextField(blank=True, help_text="md cache of the notes field")

    class Meta:
        ordering = ["declined", "applied_at"]

    def save(self, *args, **kwargs):
        self.notes_cache = compile_markdown(self.notes)
        super().save(*args, **kwargs)

