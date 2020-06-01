import os.path

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from PIL import Image

from sharinator.equipment.models import Photograph

class UploadImageTestCase(TestCase):

    def setUp(self):
        u: User = User()
        u.username = "testuser"
        u.set_password("Super_dumm_password1234")
        u.save()

    def tearDown(self):
        pass

    def test_image_metadata_stipping(self):
        pass

    def test_image_cropping(self):
        u = User.objects.get(username="testuser")
        test_image = SimpleUploadedFile( \
                name="test-image.jpg", \
                content=open("sharinator/tests/testdata/cc-test-image.jpg", "rb").read(), \
                content_type='image/jpeg')
        imgtitle="a test image"
        Photograph.objects.create(image=test_image, title=imgtitle, uploaded_by=u)
        p: Photograph = Photograph.objects.get(title=imgtitle)
        self.assertTrue(p is not None)
        self.assertTrue(p.image is not None)
        self.assertTrue(p.full_resolution_image is not None)
        self.assertTrue(p.full_resolution_image.width == 5957)
        self.assertTrue(p.full_resolution_image.height == 3971)
        self.assertTrue(p.image.width < 5957)
        self.assertTrue(p.image.height < 3971)
        self.assertTrue(os.path.isfile(p.image.path))
        self.assertTrue(os.path.isfile(p.full_resolution_image.path))
        p.delete()
        self.assertFalse(os.path.isfile(str(p.image.path)))
        self.assertFalse(os.path.isfile(str(p.full_resolution_image.path)))
        pass

