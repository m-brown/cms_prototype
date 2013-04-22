from cms_prototype.models.page_handler import PageHandler
from cms_prototype.models.site import Page
from cms_prototype.models.layout import Layout
from cms_prototype.models.blocks.text import HTMLBlock
from cms_prototype.tests.common import TemplateTestCase, strip_html_whitespace


class PreProcessHandler(PageHandler):
    def pre_block_process(self):
        b = HTMLBlock(text='bar')
        b.save()
        self.layout.items.append(b)


class PostProcessHandler(PageHandler):
    def post_block_process(self):
        self.layout.items[0].text = 'bar'


class HandlerTestCase(TemplateTestCase):

    def setUp(self):
        super(HandlerTestCase, self).setUp()
        b = HTMLBlock(text='foo')
        b.save()
        l = Layout()
        l.items.append(b)
        self.p = Page(layout=l)
        self.p.save()

    def test_non_modified_render(self):
        h = PageHandler(page=self.p)
        html = strip_html_whitespace(h.render())

        self.assertEquals(html, '<div class="layout"><div class="block">foo</div></div>')

    def test_pre_process(self):
        TestHandler = __import__('cms_prototype.tests.test_page_handler', globals(), locals(), ['PreProcessHandler'], -1).PreProcessHandler
        h = TestHandler(page=self.p)
        html = strip_html_whitespace(h.render())

        self.assertEquals(html, '<div class="layout"><div class="block">foo</div><div class="block">bar</div></div>')

    def test_post_process(self):
        TestHandler = __import__('cms_prototype.tests.test_page_handler', globals(), locals(), ['PostProcessHandler'], -1).PostProcessHandler
        h = TestHandler(page=self.p)
        html = strip_html_whitespace(h.render())

        self.assertEquals(html, '<div class="layout"><div class="block">bar</div></div>')
