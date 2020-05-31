from datetime import datetime

from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.db import models

from annoying.fields import AutoOneToOneField
from phonenumber_field.modelfields import PhoneNumberField

from sharinator.equipment.models import Photograph

# Create your models here.
class Profile(models.Model):
    user = AutoOneToOneField(User, on_delete=models.CASCADE)
    landline_number = PhoneNumberField(blank=True)
    mobile_number = PhoneNumberField(blank=True)
    additional_number = PhoneNumberField(blank=True)
    phone_numbers_visible = models.BooleanField(default=True,
            help_text="Should the phone numbers be visible to people who I leaded stuff to or from")
    profile_picture = models.ForeignKey(Photograph, null=True, on_delete=models.SET_NULL)
    pgp_key_id = models.TextField(blank=True, help_text="The key id to identify a pgp key for optional mail encryption.")
    force_logout_date = models.DateTimeField(null=True, blank=True)

    def force_logout(self):
        self.force_logout_date = datetime.now()
        self.save()

    class Meta:
        ordering = ['user']

def update_session_last_login(sender, **kwargs):
    if "request" in kwargs:
        kwargs["request"].session['LAST_LOGIN_DATE'] = datetime.now()

user_logged_in.connect(update_session_last_login)

