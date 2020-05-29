from django.contrib import admin

from sharinator.peers.models import PeerGroup, GroupApplication

# Register your models here.
admin.site.register(PeerGroup)
admin.site.register(GroupApplication)
