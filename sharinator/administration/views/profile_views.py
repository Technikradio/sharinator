from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from phonenumber_field.formfields import PhoneNumberField

from sharinator.administration.models import Profile

# Create your views here.

class ProfileEditingForm(forms.ModelForm):

    user_name = forms.CharField(label="User name:", disabled=True, required=False)
    first_name = forms.CharField(label="First name:", required=False)
    last_name = forms.CharField(label="Last name:", required=False)
    user_email = forms.EmailField(label="Email address:", required=True)

    class Meta:
        model = Profile
        localized_fields = '__all__'
        fields = ["landline_number",
                  "mobile_number",
                  "additional_number",
                  "phone_numbers_visible",
                  "pgp_key_id"]
        widgets = {
            'pgp_key_id': forms.TextInput(),
        }

class ProfileEditingView(LoginRequiredMixin, View):
    template_name = "profileediting.html"

    def check_user(self, request: HttpRequest, profile_id: int):
        p: Profile = get_object_or_404(Profile, id=profile_id)
        if not (p.user == request.user or request.user.is_superuser):
            raise PermissionDenied("This isn't your profile and you haven't the permission to edit it.")
        return p

    def get(self, request: HttpRequest, profile_id: int):
        p: Profile = self.check_user(request, profile_id)
        return render(request, self.template_name, {
            'profile': p,
            'form': ProfileEditingForm(instance=p, initial={
                'user_name': p.user.username,
                'first_name': p.user.first_name,
                'last_name': p.user.last_name,
                'user_email': p.user.email}),
        })

    def post(self, request: HttpRequest, profile_id: int):
        p: Profile = self.check_user(request, profile_id)
        form = ProfileEditingForm(request.POST)
        if form.is_valid():
            # Since there is no good alternative to user profile handling in django (yet?) we can't
            # make use of form.save(commit = False). Even https://stackoverflow.com/questions/1727564/how-to-create-a-userprofile-form-in-django-with-first-name-last-name-modificati
            # won't do the trick here so we need to do it my hand.
            p.landline_number = form.cleaned_data["landline_number"]
            p.mobile_number = form.cleaned_data["mobile_number"]
            p.additional_number = form.cleaned_data["additional_number"]
            p.phone_numbers_visible = form.cleaned_data["phone_numbers_visible"]
            p.pgp_key_id = form.cleaned_data["pgp_key_id"]
            u: User = p.user
            u.first_name = form.cleaned_data["first_name"]
            u.last_name = form.cleaned_data["last_name"]
            u.email = form.cleaned_data["user_email"]
            u.save()
            p.save()
        else:
            messages.add_message(request, messages.ERROR, 'This profile couldn\'t be edited.')
        return render(request, self.template_name, {
            'profile': p,
            'form': form,
        })

class ProfileRedirectHelperView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest):
        pid: int = request.user.profile.id
        return redirect(reverse("profileedit", args=[pid]))

class ProfileListView(LoginRequiredMixin, ListView):

    template_name = "profilelisting.html"
    paginate_by = 25
    model = Profile

    def get(self, request: HttpRequest):
        if not (request.user.is_superuser or request.user.is_staff):
            raise PermissionDenied("Sorry {}, I can't let you do that.".format(str(request.user)))
        #page: int = 1
        #if request.GET.get("page"):
        #    page = int(request.GET["page"])
        # return render(request, self.template_name, {})
        return super().get(request)

