from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.template import Context, Template

from sharinator.equipment.helpers import image as image_helper
from sharinator.equipment.models import Photograph

class ImageRenderingTestCase(TestCase):

    def render_template(self, string, context=None):
        context = context or {}
        context = Context(context)
        return Template(string).render(context)

    def setUp(self):
        pass

    def test_replace_filter(self):
        template: str = """{% load replace %}{{ "replace me"|replace:"replace me,successfully replaced" }}"""
        c = {}
        html_text = self.render_template(template, context=c)
        self.assertEquals(html_text, "successfully replaced")
        template: str = """{% load replace %}{{ "replace me"|replace:"_" }}"""
        html_text = self.render_template(template, context=c)
        self.assertEquals(html_text, "replace_me")

