from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.views.generic.base import TemplateView
from django.http import HttpRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View

class ManagementDashboardView(TemplateView, LoginRequiredMixin):

    template_name: str = "managementdashboard.html"

    def get_context_data(self, **kwargs):
        if not (self.request.user.is_superuser or self.request.user.is_staff):
            raise PermissionDenied("Only superusers and staff may access the management dashboard.")
        context = super().get_context_data(**kwargs)
        context['number_of_users'] = User.objects.all().count()
        return context

