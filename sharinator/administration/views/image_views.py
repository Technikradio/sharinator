from django import forms
from django.contrib import messages
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

class MediaEditingForm(forms.Form):
    image_title = forms.CharField(max_length=100, required=False)
    image_notes = forms.CharField(required=False, widget=forms.Textarea)

class EditMediaView(View, LoginRequiredMixin):

    template_name: str = "editmedia.html"

    def get(self, request: HttpRequest, image_id: int):
        p: Photograph = get_object_or_404(Photograph, id=image_id)
        if not (request.user.is_superuser or p.uploaded_by == request.user):
            raise PermissionDenied("You're not allowed to edit other users media files.")
        f: MediaEditingForm = MediaEditingForm(initial={'image_title': p.title, 'image_notes': p.notes})
        return render(request, self.template_name, {'form': f, 'photograph': p})

    def post(self, request, image_id: int):
        redirect_to: str = None
        if request.GET.get("redirect_to"):
            redirect_to = str(request.GET["redirect_to"])
        else:
            redirect_to = reverse("listmedia")
        p: Photograph = get_object_or_404(Photograph, id=image_id)
        if not (request.user.is_superuser or p.uploaded_by == request.user):
            raise PermissionDenied("You're not allowed to edit other users media files.")
        f: MediaEditingForm = MediaEditingForm(request.POST)
        if f.is_valid():
            p.title = f.cleaned_data["image_title"]
            p.notes = f.cleaned_data["image_notes"]
            p.save()
            return redirect(redirect_to)
        else:
            messages.add_message(request, messages.ERROR, "Your form data doesn't seam to be valid")
            return render(request, self.template_name, {'form': f, 'photograph': p})

