"""sharinator URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from sharinator.equipment.equipment_views import *

urlpatterns = [
    path('list', ListOwnEquipmentView.as_view(), name="list_equipment"),
    path('add', AddEquipmentView.as_view(), name="add_equipment"),
    path('<int:item_id>/edit', EditEquipmentView.as_view(), name="edit_equipment"),
    path('<int:item_id>/addimage', AddImageToItemView.as_view(), name="add_image_to_item"),
    path('<int:item_id>/delete', DeleteItemView.as_view(), name="delete_equipment"),
    path('<int:item_id>/show', ItemDetailView.as_view(), name="show_equipment_detail"),
]
