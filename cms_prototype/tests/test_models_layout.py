from cms_prototype.tests.common import TemplateTestCase, strip_html_whitespace
from cms_prototype.models.blocks.text import HTMLBlock
from cms_prototype.models.layout import Layout


class LayoutTest(TemplateTestCase):

    def test_id(self):
        l = Layout(html_id="foo")
        html = strip_html_whitespace(l.render())

        self.assertEqual(html, '<div id="foo" class="layout"></div>')

    def test_class(self):
        l = Layout(html_class="foo")
        html = strip_html_whitespace(l.render())

        self.assertEqual(html, '<div class="layout foo"></div>')

    def test_single_depth_single_block(self):
        b = HTMLBlock(text='foo')
        b.save()
        l = Layout()
        l.items.append(b)

        html = strip_html_whitespace(l.render())

        self.assertEqual(html, '<div class="layout"><div class="block">foo</div></div>')

    def test_single_depth_multi_block(self):
        b = HTMLBlock(text='foo')
        b.save()
        b2 = HTMLBlock(text='bar')
        b2.save()
        l = Layout()
        l.items.append(b)
        l.items.append(b2)

        html = strip_html_whitespace(l.render())

        self.assertEqual(html, '<div class="layout"><div class="block">foo</div><div class="block">bar</div></div>')

    def test_double_depth_single_blocks(self):
        b = HTMLBlock(text='foo')
        b.save()
        l = Layout()
        l.items.append(b)

        l2 = Layout()
        b2 = HTMLBlock(text='bar')
        b2.save()
        l2.items.append(b2)
        l.items.append(l2)

        html = strip_html_whitespace(l.render())

        self.assertEqual(html, '<div class="layout"><div class="block">foo</div><div class="layout"><div class="block">bar</div></div></div>')
