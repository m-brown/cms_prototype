from cms_prototype.tests.common import TemplateTestCase, strip_html_whitespace
from cms_prototype.models.blocks.link import Link


class LinkModelsTestCase(TemplateTestCase):
    def test_link_layout(self):
        l = Link(html_id='foo', html_class='bar', href='#foo', text='bar')

        html = strip_html_whitespace(l.render())
        self.assertEqual(html, '<a id="foo" href="#foo" class="bar">bar</a>')
