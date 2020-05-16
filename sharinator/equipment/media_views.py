from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.shortcuts import render, get_object_or_404
from django.views import View

from sharinator.equipment.models import Photograph

# Create your views here.
class DisplayImageView(LoginRequiredMixin, View):

    template_name: str = "display_image.html"

    def get(self, request: HttpRequest, image_id: int):
        i: Photograph = get_object_or_404(Photograph, id=image_id)
        return render(request, self.template_name, {'image': i})
