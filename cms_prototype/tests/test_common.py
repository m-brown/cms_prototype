from unittest import TestCase
from cms_prototype.tests.common import strip_html_whitespace


class TestTemplateTestCase(TestCase):
    def test_whitespace(self):
        t = '<div id="foo">         \n</div>'
        c = '<div id="foo"></div>'
        r = strip_html_whitespace(t)

        self.assertEquals(c, r)

    def test_leading_whitespace(self):
        t = '\n <div id="foo">'
        c = '<div id="foo">'
        r = strip_html_whitespace(t)

        self.assertEquals(c, r)

    def test_trailing_whitespace(self):
        t = '</div> \n'
        c = '</div>'
        r = strip_html_whitespace(t)

        self.assertEquals(c, r)

    def test_text(self):
        t = '<div id="foo">foo         \n</div>'
        c = '<div id="foo">foo</div>'
        r = strip_html_whitespace(t)

        self.assertEquals(c, r)
