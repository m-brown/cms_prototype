from cms_prototype.tests.common import TemplateTestCase, strip_html_whitespace
from cms_prototype.models.page_handler import PageHandler, process_params
from cms_prototype.models.site import Page
from cms_prototype.models.layout import Layout
from cms_prototype.models.blocks.text import HTMLBlock


WRAPPER = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <link rel="stylesheet" href="/static/bootstrap/css/bootstrap.css">
        <script src="/static/js/jquery.js"></script>
        <script src="/static/bootstrap/js/bootstrap.js"></script>
    </head>
    <body>
"""
NON_MOD_HTML = WRAPPER + """
        <div class="layout">
            <div class="block">foo</div>
        </div>
    </body>
</html>
"""

PRE_MOD_HTML = WRAPPER + """
        <div class="layout">
            <div class="block">foo</div>
            <div class="block">bar</div>
        </div>
    </body>
</html>
"""

POST_MOD_HTML = WRAPPER + """
        <div class="layout">
            <div class="block">bar</div>
        </div>
    </body>
</html>
"""


class PreProcessHandler(PageHandler):
    def pre_block_process(self):
        b = HTMLBlock(text='bar')
        b.save()
        self.page.layout.items.append(b)


class PostProcessHandler(PageHandler):
    def post_block_process(self):
        self.page.layout.items[0].text = 'bar'


class Handler(TemplateTestCase):
    def setUp(self):
        super(TemplateTestCase, self).setUp()
        b = HTMLBlock(text='foo')
        b.save()
        l = Layout()
        l.items.append(b)
        self.p = Page(layout=l)
        self.p.save()

    def test_non_modified_render(self):
        h = PageHandler(page=self.p, inferred={}, get={}, post={})
        h.pre_block_process()
        h.block_process()
        h.post_block_process()
        html = strip_html_whitespace(h.render())

        self.assertEquals(html, strip_html_whitespace(NON_MOD_HTML))

    def test_pre_process(self):
        TestHandler = __import__('cms_prototype.tests.test_page_handler', globals(), locals(), ['PreProcessHandler'], -1).PreProcessHandler
        h = TestHandler(page=self.p, inferred={}, get={}, post={})
        h.pre_block_process()
        h.block_process()
        h.post_block_process()
        html = strip_html_whitespace(h.render())

        self.assertEquals(html, strip_html_whitespace(PRE_MOD_HTML))

    def test_post_process(self):
        TestHandler = __import__('cms_prototype.tests.test_page_handler', globals(), locals(), ['PostProcessHandler'], -1).PostProcessHandler
        h = TestHandler(page=self.p, inferred={}, get={}, post={})
        h.pre_block_process()
        h.block_process()
        h.post_block_process()
        html = strip_html_whitespace(h.render())

        self.assertEquals(html, strip_html_whitespace(POST_MOD_HTML))


class ProcessParams(TemplateTestCase):
    def test_simple(self):
        ans = process_params({'foo': 'foo'}, {'bar': 'bar'}, {'buz': 'buz'})

        self.assertDictEqual(ans, {'foo': 'foo', 'bar': 'bar', 'buz': 'buz'})

    def test_overwrite(self):
        ans = process_params({'foo': 'foo'}, {'foo': 'bar'}, {'foo': 'buz'})

        self.assertDictEqual(ans, {'foo': 'foo'})
