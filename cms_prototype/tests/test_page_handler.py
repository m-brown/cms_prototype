from pyramid import testing
from cms_prototype.tests.common import TemplateTestCase, strip_html_whitespace
from cms_prototype.models.page_handler import PageHandler
from cms_prototype.models.site import Page, Url
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
        self.request.url.page.layout.items.append(b)


class PostProcessHandler(PageHandler):
    def post_block_process(self):
        self.request.url.page.layout.items[0].text = 'bar'


class Handler(TemplateTestCase):
    def setUp(self):
        super(TemplateTestCase, self).setUp()
        b = HTMLBlock(text='foo')
        b.save()
        l = Layout()
        l.items.append(b)
        self.p = Page(layout=l)
        self.p.save()

        self.request = testing.DummyRequest()
        self.request.url = Url(page=self.p)

    def test_non_modified_render(self):
        h = PageHandler(request=self.request)
        h.pre_block_process()
        h.block_process()
        h.post_block_process()
        html = strip_html_whitespace(h.render())

        self.assertEquals(html, strip_html_whitespace(NON_MOD_HTML))

    def test_pre_process(self):
        TestHandler = __import__('cms_prototype.tests.test_page_handler', globals(), locals(), ['PreProcessHandler'], -1).PreProcessHandler
        h = TestHandler(request=self.request)
        h.pre_block_process()
        h.block_process()
        h.post_block_process()
        html = strip_html_whitespace(h.render())

        self.assertEquals(html, strip_html_whitespace(PRE_MOD_HTML))

    def test_post_process(self):
        TestHandler = __import__('cms_prototype.tests.test_page_handler', globals(), locals(), ['PostProcessHandler'], -1).PostProcessHandler
        h = TestHandler(request=self.request)
        h.pre_block_process()
        h.block_process()
        h.post_block_process()
        html = strip_html_whitespace(h.render())

        self.assertEquals(html, strip_html_whitespace(POST_MOD_HTML))

    def test_form_post_update(self):
        from cms_prototype.models.blocks.form import MongoEngineForm, Input
        from cms_prototype.models.blocks.link import Link
        l = Link(href="foo", text="bar")
        l.save()

        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            fields=[Input(type='text', name='href'),
                                    Input(type='text', name='text')],
                            identity={'labelID': 'id'})
        f.save()
        self.p.layout.items.append(f)
        self.p.save()

        self.request.POST = {'labelID': l.id, 'text': 'buz'}
        h = PageHandler(request=self.request)
        h.pre_block_process()
        h.block_process()
        h.post_block_process()
        h.render()

        l = Link.objects.get(id=l.id)

        self.assertEquals(l.text, 'buz')

    def test_form_post_create_object(self):
        from cms_prototype.models.blocks.form import MongoEngineForm, Input
        from cms_prototype.models.blocks.link import Link

        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            fields=[Input(type='text', name='href'),
                                    Input(type='text', name='text')],
                            identity={'labelID': 'id'})
        f.save()
        self.p.layout.items.append(f)
        self.p.save()

        #a page load should not create anything
        h = PageHandler(request=self.request)
        h.pre_block_process()
        h.block_process()
        h.post_block_process()
        h.render()

        self.assertEquals(Link.objects.count(), 0)

        #a post should create the object
        self.request.POST = {'href': 'foo', 'text': 'bar'}
        h = PageHandler(request=self.request)
        h.pre_block_process()
        h.block_process()
        h.post_block_process()
        h.render()

        self.assertEquals(Link.objects.count(), 1)
        l = Link.objects.get()
        self.assertEquals(l['href'], 'foo')
        self.assertEquals(l['text'], 'bar')

        #a simple reload should not create anything
        self.request.POST = {}
        h = PageHandler(request=self.request)
        h.pre_block_process()
        h.block_process()
        h.post_block_process()
        h.render()

        self.assertEquals(Link.objects.count(), 1)
