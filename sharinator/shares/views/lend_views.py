import datetime

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpRequest
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import FormView

from sharinator.equipment.models import Item
from sharinator.shares.models import Lending

# Create your views here.
class LendForm(forms.ModelForm):
    class Meta:
        model = Lending
        localized_fields = '__all__'
        fields = ["start_of_lending", "end_of_lending", "notes"]
        widgets = {"notes": forms.Textarea()}

class LendEquipmentView(LoginRequiredMixin, FormView):
    template_name: str = "lend.html"
    form_class = LendForm
    success_url = "/"
    item: Item = None

    def get(self, request: HttpRequest, item_id: int):
        self.item = get_object_or_404(Item, id=item_id)
        return super().get(request)

    def post(self, request: HttpRequest, item_id: int):
        self.item = get_object_or_404(Item, id=item_id)
        return super().post(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item'] = self.item
        return context

    def form_valid(self, form):
        try:
            Lending.objects.create(lending_user=self.request.user,
                    item_to_lend=self.item,
                    start_of_lending=form.cleaned_data["start_of_lending"],
                    end_of_lending=form.cleaned_data["end_of_lending"],
                    notes=form.cleaned_data["notes"])
        except ValidationError as e:
            messages.add_message(self.request, messages.ERROR, "Failed to request item: {}".format(e))
            return render(self.request, self.template_name, self.get_context_data())
        messages.add_message(self.request, messages.SUCCESS, "Successfully lended item.")
        self.success_url = reverse("mylends")
        if self.request.GET.get("redirect_to"):
            self.success_url = str(self.request.GET["redirect_to"])
        return super().form_valid(form)


class MyLendsView(LoginRequiredMixin, TemplateView):

    template_name = "mylendings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_futur_lendings = Lending.objects.all().filter(lending_user=self.request.user).filter(end_of_lending__gte=datetime.date.today()).order_by("start_of_lending")[:1000]
        context["more_future_lendings"] = (len(my_futur_lendings) > 998)
        last_lending: Lending = my_futur_lendings[0]
        lend_groups = []
        if last_lending:
            lend_groups.append([])
        for l in my_futur_lendings:
            if last_lending.start_of_lending == l.start_of_lending:
                lend_groups[-1].append(l)
            else:
                lend_groups.append([l])
            last_lending = l
        context["future_lend_groups"] = lend_groups
        return context

