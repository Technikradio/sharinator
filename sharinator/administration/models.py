from django.contrib.auth.models import User
from django.db import models

from phonenumber_field.modelfields import PhoneNumberField

from sharinator.equipment.models import Photograph

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    landline_number = PhoneNumberField(blank=True)
    mobile_number = PhoneNumberField(blank=True)
    additional_number = PhoneNumberField(blank=True)
    phone_numbers_visible = models.BooleanField(default=True,
            help_text="Should the phone numbers be visible to people who I leaded stuff to or from")
    profile_picture = models.ForeignKey(Photograph, null=True, on_delete=models.SET_NULL)
    pgp_key_id = models.TextField(blank=True, help_text="The key id to identify a pgp key for optional mail encryption.")

