from django.test import TestCase

from sharinator.equipment.helpers.markdown import compile_markdown

# Create your tests here.
class TestMarkdownCompiling(TestCase):

    def test_general_compiling(self):
        self.assertEquals(compile_markdown("# Test MD"),
                          '<h1 id="test-md">Test MD</h1>')

    def test_html_insertion_prevention(self):
        compiled_md = compile_markdown("<htmlinsert />")
        print(compiled_md)
        self.assertFalse("<" in compiled_md.replace("<p>", "").replace("</p>", ""))
        self.assertFalse(">" in compiled_md.replace("<p>", "").replace("</p>", ""))
        self.assertTrue("&gt;" in compiled_md)
        self.assertTrue("&lt;" in compiled_md)

