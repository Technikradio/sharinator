import datetime

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import FormView

from sharinator.administration.views.image_views import SelectImageView
from sharinator.administration.views.confirm_view import ConfirmingView
from sharinator.equipment.models import Item, Photograph

# Create your views here.
class ListOwnEquipmentView(ListView, LoginRequiredMixin):

    template_name: str = "listownequipment.html"
    paginate_by: int = 25

    def get_queryset(self):
        queryset = Item.objects.all().filter(parent_container=None)
        if not ((self.request.user.is_staff or self.request.user.is_superuser) and self.request.GET.get("global")):
            queryset = queryset.filter(owner=self.request.user)
        return queryset.order_by("name").order_by("owner")


class EditEquipmentForm(forms.ModelForm):
    class Meta:
        model = Item
        localized_fields = '__all__'
        fields = ["name",
                "visible_to_others",
                "is_container",
                "can_be_lend_alone",
                "notes"]
        widgets = {
                "notes": forms.Textarea()}


class AddEquipmentView(FormView, LoginRequiredMixin):

    template_name: str = "additem.html"
    form_class = EditEquipmentForm
    success_url = "/"

    def form_valid(self, form):
        i: Item = Item.objects.create(owner=self.request.user,
                notes=form.cleaned_data["notes"],
                name=form.cleaned_data["name"],
                visible_to_others=form.cleaned_data["visible_to_others"],
                is_container=form.cleaned_data["is_container"],
                can_be_lend_alone=form.cleaned_data["can_be_lend_alone"])
        self.success_url = reverse("edit_equipment", args=[i.id])
        messages.add_message(self.request, messages.SUCCESS, "Successfully added item.")
        return super().form_valid(form)

class EditEquipmentView(FormView, LoginRequiredMixin):

    template_name: str = "edititem.html"
    form_class = EditEquipmentForm
    success_url = "/"

    item_id: int = -1
    item: Item = None

    def get_form(self):
        if self.request.POST:
            return self.form_class(self.request.POST)
        return self.form_class(instance=self.item)

    def form_valid(self, form):
        i: Item = self.item
        i.name = form.cleaned_data["name"]
        i.notes = form.cleaned_data["notes"]
        i.visible_to_others = form.cleaned_data["visible_to_others"]
        i.is_container = form.cleaned_data["is_container"]
        i.can_be_lend_alone = form.cleaned_data["can_be_lend_alone"]
        i.save()
        self.success_url = reverse("edit_equipment", args=[self.item_id])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item'] = self.item
        return context

    def check_permissions(self, request: HttpRequest):
        i: Item = get_object_or_404(Item, id=self.item_id)
        if not(i.owner == request.user or request.user.is_superuser or request.user.is_staff):
            raise PermissionDenied("You're not allowed to edit other users items.")
        self.item = i

    def get(self, request: HttpRequest, item_id: int):
        self.item_id = item_id
        self.check_permissions(request)
        return super().get(request)

    def post(self, request: HttpRequest, item_id: int):
        self.item_id = item_id
        self.check_permissions(request)
        return super().post(request)

class AddImageToItemView(SelectImageView, LoginRequiredMixin):
            
    item_id: int = -1

    def get(self, request: HttpRequest, item_id: int):
        self.item_id = item_id
        self.redirect_to = reverse("edit_equipment", args=[self.item_id])
        self.redirect_on_cancle = reverse("edit_equipment", args=[self.item_id])
        return super().get(request)
            
    def post(self, request: HttpRequest, item_id: int):
        self.item_id = item_id
        self.redirect_to = reverse("edit_equipment", args=[self.item_id])
        self.redirect_on_cancle = reverse("edit_equipment", args=[self.item_id])
        return super().post(request)

    def get_payload_data(self, request: HttpRequest):
        self.show_only_own_images = not (self.request.user.is_superuser or self.request.user.is_staff)
        return str(self.item_id)
                        
    def process_selection(self, request: HttpRequest, image: Photograph, payload: str):
        i: Item = get_object_or_404(Item, id=self.item_id)
        if i.owner != request.user and not (request.user.is_superuser or request.user.is_staff):
            raise PermissionDenied("You're not allowed to add images to this item.")
        i.images.add(image)
        i.save()
        messages.add_message(request, messages.SUCCESS, \
                "Successfully added image '{}' to item.".format(str(image.title)))

class DeleteItemView(ConfirmingView, LoginRequiredMixin):

    message = "Are you sure you want to delete this item?"

    item_id: int = -1

    def get(self, request: HttpRequest, item_id: int):
        self.item_id = item_id
        return super().get(request)

    def post(self, request: HttpRequest, item_id: int):
        self.item_id = item_id
        return super().post(request)

    def prepare(self, request: HttpRequest):
        self.redirect_to = reverse("list_equipment")
        self.safe_link = reverse("edit_equipment", args=[self.item_id])

    def perform_action(self, request: HttpRequest):
        i: Item = get_object_or_404(Item, id=self.item_id)
        if not (i.owner == request.user or request.user.is_superuser):
            raise PermissionDenied("You're not allowed to delete other users property.")
        i.delete()
        messages.add_message(request, messages.SUCCESS, "Successfully deleted item '{}'".format(i.name))

class ItemDetailView(View, LoginRequiredMixin):

    template_name: str = "display_item.html"

    def get(self, request: HttpRequest, item_id: int):
        i: Item = get_object_or_404(Item, id=item_id)
        if not (request.user.is_superuser or request.user.is_staff or request.user == i.owner):
            raise PermissionDenied("Unfortunately this is for her Majesty's eyes only.")
        upcomming_lendings = i.lendings.filter(start_of_lending__gte=datetime.date.today()).order_by("start_of_lending")
        # since django querys are lazy doing the limit below is safe
        past_lendings = i.lendings.filter(end_of_lending__lt=datetime.date.today()).order_by("-end_of_lending")[:10]
        return render(request, self.template_name, {
            "item": i,
            "upcomming_lendings": upcomming_lendings,
            "past_lendings": past_lendings})

