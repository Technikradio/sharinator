from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from sharinator.equipment.helpers import image as image_helper
from sharinator.equipment.models import Photograph

class ImageRenderingTestCase(TestCase):

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

    def test_image_large_rendering(self):
        i: Photograph = Photograph.objects.get(title="An image to display")
        icon_html_text = image_helper.render_as_large_image(i)
        self.assertTrue("rendering-test-image" in icon_html_text)

