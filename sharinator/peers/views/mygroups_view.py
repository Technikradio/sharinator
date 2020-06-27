from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views.generic import ListView

from sharinator.peers.models import PeerGroup

# Create your views here.
class MyGroupsView(LoginRequiredMixin, ListView):
    
    template_name: str = "mygroups.html"
    paginate_by: int = 50

    def get_queryset(self):
        return self.request.user.member_of_peergroups.all()

