import datetime
import os

from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

import magic

from PIL import Image

from sharinator.equipment.helpers.markdown import compile_markdown

# Shamelessly inspired by the hagrid gallery
class Photograph(models.Model):
    image = models.ImageField(upload_to="images/%Y/%m/",
            help_text="The image to display everywhere (cropped)")
    full_resolution_image = models.ImageField(upload_to="images/fullres/%Y/%m/", null=True,
            blank=True, help_text="A full resolution copy of the image for close up looks")
    title = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True, help_text="optional markdown notes on the image")
    notes_cache = models.TextField(blank=True, help_text="md cache of the notes field")
    uploaded_by = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    uploaded_at = models.DateField(editable=False, default=datetime.date.today, help_text="Date of creation")

    def __str__(self):
        return "Image '{}' uploaded by {}".format(self.title, str(self.uploaded_by))

    class Meta:
        ordering = ["uploaded_at"]

    def save(self, *args, **kwargs):
        self.notes_cache = compile_markdown(self.notes)
        super().save(*args, **kwargs)
        if not self.image:
            return
        if not self.full_resolution_image:
            self.full_resolution_image = SimpleUploadedFile( \
                    name=os.path.basename(self.image.path), \
                    content=open(self.image.path, 'rb').read(), \
                    content_type=magic.from_file(self.image.path, mime=True))
            self.save()
            return
        else:
            # Resize image
            image = Image.open(str(self.full_resolution_image.path))
            w, h = image.size
            while w * h > 2 * 10**6:
                w, h = w // 2, h // 2
            image = image.resize((w, h), Image.ANTIALIAS)
            image.save(str(self.image.path), 'PNG', quality=80)

@receiver(post_delete, sender=Photograph)
def photograph_post_delete_handler(sender, **kwargs):
    p = kwargs['instance']
    storage, path = p.full_resolution_image.storage, p.full_resolution_image.path
    storage.delete(path)
    storage, path = p.image.storage, p.image.path
    storage.delete(path)

class Item(models.Model):
    name = models.CharField(max_length=100, help_text="The name of the container")
    notes = models.TextField(blank=True, help_text="Thoughts on the container")
    notes_cache = models.TextField(blank=True, help_text="md chache of the notes field")
    visible_to_others = models.BooleanField(default=True, help_text="If this is set to false "\
            "only the owner can see this container. Even if it is set to true only members of his "\
            "peer group can see this container")
    parent_container = models.ForeignKey("self", null=True, default=None, on_delete=models.SET_NULL)
    images = models.ManyToManyField(Photograph)
    created_at = models.DateField(editable=False, default=datetime.date.today, help_text="Date of creation")
    owner = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    is_container = models.BooleanField(default=False, help_text="If true this item can contain other items.")
    can_be_lend_alone = models.BooleanField(default=True, help_text="If false one can only lend the parent container.")

    def save(self, *args, **kwargs):
        if self.parent_container != None:
            if not self.parent_container.is_container:
                raise ValidationError("The selected parent isn't a container")
        self.notes_cache = compile_markdown(self.notes)
        super().save(*args, **kwargs)

