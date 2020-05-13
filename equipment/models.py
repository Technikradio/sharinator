import datetime

from django.contrib.auth.models import User
from django.db import models

from PIL import Image


# Shamelessly inspired by the hagrid gallery
class Photograph(models.Model):
    image = models.ImageField(upload_to="images/%Y/%m/",
            help_text="The image to display everywhere (cropped)")
    full_resolution_image = models.ImageField(upload_to="images/fullres/%Y/%m/", null=True,
            help_text="A full resolution copy of the image for close up looks")
    title = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True, help_text="optional markdown notes on the image")
    uploaded_by = models.ForeignKey(User, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return "Image '{}' uploaded by {}".format(self.title, str(self.uploaded_by))

    def save(self, *args, **kwargs):
        if self.full_resolution_image == None:
            self.full_resolution_image = self.image
        super().save(*args, **kwargs)
        if not self.image:
            return

        # Strip metadata off full res image
        image_with_meta = Image.open(str(self.full_resolution_image.path))
        data = list(image_with_meta.getdata())
        image = Image.new(image_with_meta.mode, image_with_meta.size)
        image.save(str(self.full_resolution_image.path), 'PNG')

        # Resize image
        image_with_meta = Image.open(str(self.image.path))
        data = list(image_with_meta.getdata())
        image = Image.new(image_with_meta.mode, image_with_meta.size)
        image.putdata(data)
        w, h = image.size
        while w * h > 2 * 10**6:
            w, h = w // 2, h // 2
        image = image.resize((w, h), Image.ANTIALIAS)
        image.save(str(self.image.path), 'PNG')


class Container(models.Model):
    name = models.CharField(max_length=100, help_text="The name of the container")
    notes = models.TextField(blank=True, help_text="Thoughts on the container")
    visible_to_others = models.BooleanField(default=True, help_text="If this is set to false "\
            "only the owner can see this container. Even if it is set to true only members of his "\
            "peer group can see this container")
    parent_container = models.ForeignKey("self", null=True, default=None, on_delete=models.SET_NULL)
    images = models.ManyToManyField(Photograph)
    created_at = models.DateField(editable=False, default=datetime.date.today, help_text="Date of creation")


class Item(models.Model):
    name = models.CharField(max_length=100, help_text="The name of the item")
    notes = models.TextField(blank=True, help_text="Thoughts on the item (markdown)")
    container = models.ForeignKey(Container, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    images = models.ManyToManyField(Photograph)
    owner = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    created_at = models.DateField(editable=False, default=datetime.date.today, help_text="Date of creation")

