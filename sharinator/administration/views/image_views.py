from abc import ABC, abstractmethod

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

from sharinator.administration.views.confirm_view import ConfirmingView
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

class SingleMediaUploadForm(forms.Form):
    image_file = forms.ImageField()
    image_title = forms.CharField(max_length=100, required=False)
    image_notes = forms.CharField(required=False, widget=forms.Textarea)

class MassMediaUploadForm(forms.Form):
    image_files = forms.ImageField()
    title_template = forms.CharField(max_length=100, required=False)
    notes_template = forms.CharField(required=False, widget=forms.Textarea)

class SingleMediaUploadView(View, LoginRequiredMixin):

    template_name = "imageupload.html"

    def get(self, request: HttpRequest):
        f: SingleMediaUploadForm = SingleMediaUploadForm()
        return render(request, self.template_name, {
            'form': f,
            'single': True,
            })

    def post(self, request: HttpRequest):
        f: SingleMediaUploadForm = SingleMediaUploadForm(request.POST, request.FILES)
        redirect_to: str = None
        if request.GET.get("redirect_to"):
            redirect_to = str(request.GET["redirect_to"])
        else:
            redirect_to = reverse("listmedia")
        if f.is_valid():
            Photograph.objects.create(title=f.cleaned_data["image_title"],
                    notes=f.cleaned_data["image_notes"],
                    uploaded_by=request.user,
                    image=f.cleaned_data["image_file"])
            return redirect(redirect_to)
        else:
            messages.add_message(request, messages.ERROR, "Unable to upload image due to invalid form data.")
            return render(request, self.template_name, {
                'form': f,
                'single': True,
                })

class MassMediaUploadView(View, LoginRequiredMixin):

    template_name = "imageupload.html"

    def get(self, request: HttpRequest):
        f: MassMediaUploadForm = MassMediaUploadForm()
        return render(request, self.template_name, {
            'form': f,
            'single': False,
            })

    def post(self, request: HttpRequest):
        f: MassMediaUploadForm = MassMediaUploadForm(request.POST, request.FILES)
        redirect_to: str = None
        if request.GET.get("redirect_to"):
            redirect_to = str(request.GET["redirect_to"])
        else:
            redirect_to = reverse("listmedia")
        if f.is_valid():
            for p in f.cleaned_data["image_files"]:
                Photograph.objects.create(title=f.cleaned_data["title_template"].format(str(p.path)),
                        notes=f.cleaned_data["notes_template"].format(str(p.path)),
                        image=p)
            return redirect(redirect_to)
        else:
            messages.add_message(request, messages.ERROR, "Unable to upload image due to invalid form data.")
            return render(request, self.template_name, {
                'form': f,
                'single': False,
                })


class ImageSelectionForm(forms.Form):
    image_id = forms.IntegerField(widget=forms.HiddenInput())
    payload = forms.CharField(widget=forms.HiddenInput())

class SelectImageView(View, ABC):

    template_name = "selectimage.html"

    message: str = "Please select an image."
    redirect_to: str = "/"
    redirect_on_cancle: str = "/"
    show_only_own_images: bool = True

    def get(self, request: HttpRequest):
        # Use extracted function so that the get method can be overwritten safely
        return self.perform_get(request)

    def perform_get(self, request: HttpRequest):
        payload = self.get_payload_data(request)
        qs = Photograph.objects.all()
        if self.show_only_own_images:
            qs = qs.filter(uploaded_by=request.user)
        # We're not using a form for rendering here since it's unnessessary
        # and would result in a huge amount of memory being consumed.
        return render(request, self.template_name, {
            'message': self.message,
            'safe_link': self.redirect_on_cancle,
            'payload': payload,
            'images': qs
            })

    def post(self, request: HttpRequest):
        f: ImageSelectionForm = ImageSelectionForm(request.POST)
        if not f.is_valid():
            messages.add_message(request, messages.ERROR, "Failed to verify image selection.")
            return self.perform_get(request)
        pid: int = int(f.cleaned_data["image_id"])
        p: Photograph = get_object_or_404(Photograph, id=pid)
        if (not self.show_only_own_images or request.user.is_superuser or request.user.is_staff) and p.uploaded_by != request.user:
            raise PermissionDenied("You're not allowed to use this image.")
        self.process_selection(request, p, f.cleaned_data["payload"])
        return redirect(self.redirect_to)

    @abstractmethod
    def get_payload_data(self, request: HttpRequest) -> str:
        pass

    @abstractmethod
    def process_selection(self, request: HttpRequest, image: Photograph, payload: str):
        pass


class DeleteImageView(LoginRequiredMixin, ConfirmingView):
    
    message = "Are you sure you want to delete this image?"

    def prepare(self, request: HttpRequest):
        self.safe_link = reverse("listmedia")
        self.redirect_to = reverse("listmedia")

    def perform_action(self, request: HttpRequest):
        if not request.GET.get("image_id"):
            messages.add_message(request, messages.ERROR, 'There was no image_id supplied.')
            return
        p: Photograph = get_object_or_404(Photograph, id=int(request.GET["image_id"]))
        if not (p.uploaded_by == request.user or request.user.is_superuser or request.user.is_staff):
            raise PermissionDenied("Maybe the other users don't want their pictures deleted?")
        p.delete()
        messages.add_message(request, messages.SUCCESS, "Successfully deleted image #{}.".format(request.GET["image_id"]))

