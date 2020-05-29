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
        u: User = User()
        u.username = "testme"
        u.save()
        Photograph.objects.create(image=SimpleUploadedFile( \
                name="rendering-test-image.jpg", \
                content=open("sharinator/tests/testdata/cc-test-image.jpg", "rb").read(), \
                content_type='image/jpeg'), title="An image to display", \
                uploaded_by=u)

    def test_image_icon_rendering(self):
        i: Photograph = Photograph.objects.get(title="An image to display")
        icon_html_text = image_helper.render_as_icon(i)
        self.assertTrue("rendering-test-image" in icon_html_text)
        self.assertTrue("width:32px;height:32px;" in icon_html_text)
        self.assertTrue("/icons/missing-picture.svg" in image_helper.render_as_icon(None))

    def test_image_large_rendering(self):
        i: Photograph = Photograph.objects.get(title="An image to display")
        icon_html_text = image_helper.render_as_large_image(i)
        self.assertTrue("rendering-test-image" in icon_html_text)
        self.assertTrue("/icons/missing-picture.svg" in image_helper.render_as_large_image(None))

    def test_template_tags(self):
        p: Photograph = Photograph.objects.get(title="An image to display")
        template: str = """
            {% load image_rendering %}
            {% render_image photo %}"""
        c = {}
        c["photo"] = p
        icon_html_text = self.render_template(template, context=c)
        self.assertTrue("rendering-test-image" in icon_html_text)
        self.assertTrue(icon_html_text.lstrip().startswith("<a ")) # Test for propper HTML (escaping!)
        template = template.replace("render_image", "render_icon")
        c["photo"] = None
        icon_html_text = self.render_template(template, context=c)
        self.assertTrue("<a" not in icon_html_text)

