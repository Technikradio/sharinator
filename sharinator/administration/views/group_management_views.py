from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views.generic import ListView
from django.views.generic.edit import CreateView

from sharinator.peers.models import PeerGroup

# Create your views here.
class ListAllGroupsView(LoginRequiredMixin, ListView):

    template_name: str = "listallgroups.html"
    paginate_by: int = 50

    def get_queryset(self):
        if not (self.request.user.is_superuser or self.request.user.is_staff):
            raise PermissionDenied("Only admins may administrate groups.")
        return PeerGroup.objects.all()


class AddGroupView(LoginRequiredMixin, CreateView):
    template_name = "addgroup.html"

    model = PeerGroup
    fields = ["name", "visible_to_strangers", "notes"]

    def get_absolute_url(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return reverse("admlistallgroups")
        else:
            return reverse("mygroups")

    def form_valid(self, form):
        # Since we've to decide where to redirect to based
        # on the current user we call get_absolute_url now
        self.success_url = self.get_absolute_url()
        # After doing so we let django create the object
        response = super().form_valid(form)
        # This should create the group inside self.object
        group: PeerGroup = self.object
        # Now we add the current user as a member and an admin
        group.members.add(self.request.user)
        group.admins.add(self.request.user)
        # And save the group
        group.save()
        # Now we give back the control to django
        return response
