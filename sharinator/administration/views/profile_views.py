import logging

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from phonenumber_field.formfields import PhoneNumberField

from sharinator.administration.models import Profile
from sharinator.administration.views.confirm_view import ConfirmingView

logger = logging.getLogger(__name__)

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

class DeleteUserView(ConfirmingView, LoginRequiredMixin):

    message = "Are you sure you want to delete this profile?"

    def prepare(self, request: HttpRequest):
        self.safe_link = reverse("profileeditredirector")

    def perform_action(self, request: HttpRequest):
        if not request.GET.get("user_id"):
            messages.add_message(request, messages.ERROR, 'There was no user_id supplied.')
            return
        user_id: int = int(request.GET["user_id"])
        u: User = get_object_or_404(User, id=user_id)
        if not (request.user.is_superuser or u == request.user):
            raise PermissionDenied("You can't simply delete other users. That's not nice.")
        username: str = str(u.username)
        u.delete() # This should also delete the profile and all added stuff.
        messages.add_message(request, messages.SUCCESS, \
                "Goodby {}. We'll miss you. Account successfully deleted.".format(username))

class OOBUserLogoutView(ConfirmingView, LoginRequiredMixin):

    message = "Are you sure you want to log this user out?"

    def prepare(self, request: HttpRequest):
        self.safe_link = reverse("profilelist")

    def perform_action(self, request: HttpRequest):
        if not (request.user.is_superuser or request.user.is_staff):
            raise PermissionDenied("Dear {}, didn't your parents told you to not log other users out?" \
                    .format(str(request.user.username)))
        if not request.GET.get("user_id"):
            messages.add_message(request, messages.ERROR, 'There was no user_id supplied.')
            return
        user_id: int = int(request.GET["user_id"])
        u: User = get_object_or_404(User, id=user_id)
        u.profile.force_logout()
        messages.add_message(request, messages.SUCCESS,
                "Successfully logged user '{}' out.".format(u.username))

class AddUserForm(forms.Form):

    user_name = forms.CharField(label="User name: ")
    user_email = forms.EmailField(label="Email address: ")
    user_password = forms.CharField(label="Password: ", widget=forms.PasswordInput())
    user_password_confirm = forms.CharField(label="Confirm Password: ", widget=forms.PasswordInput())

class AddUserView(View, LoginRequiredMixin):

    """
    As for now one needs to be a user on the site to 'invite other users. This will change dough.'
    """

    template_name: str = "adduser.html"
    goto_after: str = "profilelist"

    def get(self, request: HttpRequest):
        form = AddUserForm()
        return render(request, self.template_name, {
            'form': form,
            })

    def post(self, request: HttpRequest):
        form = AddUserForm(request.POST)
        if not form.is_valid():
            messages.add_message(request, messages.ERROR, "Invalid form.")
        user_name: str = form.cleaned_data["user_name"]
        user_email: str = form.cleaned_data["user_email"]
        user_password: str = form.cleaned_data["user_password"]
        user_password_confirm: str = form.cleaned_data["user_password_confirm"]
        if User.objects.filter(username=user_name).count() > 0:
            messages.add_message(request, messages.ERROR, "A user '{}' already exists.".format(user_name))
            return render(request, self.template_name, {
                'form': form,
                })
        if user_password != user_password_confirm:
            messages.add_message(request, messages.ERROR, "Passwords don't match")
            return render(request, self.template_name, {
                'form': form,
                })
        try:
            User.objects.create_user(username=user_name, email=user_email, password=user_password)
            logger.info("Added user: " + str(User.objects.get(username=user_name).profile))
        except Exception as e:
            messages.add_message(request, messages.ERROR, "Error on adding user: " + str(e))
        messages.add_message(request, messages.SUCCESS, \
                "Successfully added user {}. You may now edit its profile.".format(user_name))
        return redirect(reverse(self.goto_after))

