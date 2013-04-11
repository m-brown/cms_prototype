from cms_prototype.tests.common import TestCase
from cms_prototype.models.page_handler import PageHandler
from cms_prototype.models.site import Page
from cms_prototype.models.layout import Layout
from cms_prototype.models.blocks.text import HTMLBlock


class Handler(TestCase):

    def test_non_modified_render(self):
        l = Layout()
        l.items.append(HTMLBlock(text='foo'))
        p = Page(layout=l)

        h = PageHandler(page=p)
        html = h.render()

        self.assertEquals(html, '<div class="layout">\n<div class="block">\nfoo\n</div>\n</div>')
