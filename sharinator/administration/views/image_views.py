from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from sharinator.equipment.models import Photograph

class ListMediaView(ListView, LoginRequiredMixin):

    template_name: str = "listmedia.html"
    paginate_by = 125

    def get_queryset(self):
        queryset = Photograph.objects.all()
        if not ((self.request.user.is_superuser or self.request.user.is_staff) and self.request.GET.get("global")):
            queryset = queryset.filter(uploaded_by=self.request.user)
        return queryset.order_by("uploaded_at")

