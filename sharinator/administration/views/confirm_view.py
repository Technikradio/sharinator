from abc import ABC, abstractmethod
from uuid import uuid4

from django import forms
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.views import View

class ConfirmForm(forms.Form):
    action_uuid = forms.UUIDField(initial=uuid4())

    class Meta:
        widgets = {'action_uuid': forms.HiddenInput()}

class ConfirmingView(View, ABC):

    template_name = "confirmaction.html"

    message: str = "The action you're about to order might have severe consequences. Are you sure you want to proceed?"
    title: str = "Please confirm your action."
    redirect_to: str = "/"
    safe_link: str = "/"

    def get(self, request: HttpRequest):
        self.prepare(request)
        form = ConfirmForm()
        return render(request, self.template_name, {
            'message': self.message,
            'title': self.title,
            'safe_link': self.safe_link,
            'form': form})

    def post(self, request: HttpRequest):
        self.prepare(request)
        form = ConfirmForm(request.POST)
        if form.is_valid():
            self.perform_action(request)
        return redirect(self.redirect_to)

    def prepare(self, request: HttpRequest):
        pass

    @abstractmethod
    def perform_action(self, request: HttpRequest):
        pass

