# Generated by Django 3.0.6 on 2020-05-15 17:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('equipment', '0001_Initial_Model'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('landline_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('mobile_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('additional_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('phone_numbers_visible', models.BooleanField(default=True, help_text='Should the phone numbers be visible to people who I leaded stuff to or from')),
                ('pgp_key_id', models.TextField(blank=True, help_text='The key id to identify a pgp key for optional mail encryption.')),
                ('profile_picture', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='equipment.Photograph')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]