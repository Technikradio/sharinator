from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView

from sharinator.equipment.models import Item

# Create your views here.
class ListOwnEquipmentView(ListView, LoginRequiredMixin):

    template_name: str = "listownequipment.html"
    paginate_by: int = 25

    def get_queryset(self):
        queryset = Item.objects.all().filter(parent_container=None)
        if not ((self.request.user.is_staff or self.request.user.is_superuser) and self.request.GET.get("global")):
            queryset = queryset.filter(owner=self.request.user)
        return queryset.order_by("name").order_by("owner")
