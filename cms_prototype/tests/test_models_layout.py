from cms_prototype.tests.common import TemplateTestCase
from cms_prototype.models.blocks.text import HTMLBlock
from cms_prototype.models.layout import Layout


class LayoutTest(TemplateTestCase):

    def test_id(self):
        l = Layout(html_id="foo")
        html = l.render()

        self.assertEqual(html, '<div id="foo" class="layout">\n</div>')

    def test_class(self):
        l = Layout(html_class="foo")
        html = l.render()

        self.assertEqual(html, '<div class="layout foo">\n</div>')

    def test_single_depth_single_block(self):
        b = HTMLBlock(text='foo')
        b.save()
        l = Layout()
        l.items.append(b)

        html = l.render()

        self.assertEqual(html, '<div class="layout">\n<div class="block">\nfoo\n</div>\n</div>')

    def test_single_depth_multi_block(self):
        b = HTMLBlock(text='foo')
        b.save()
        b2 = HTMLBlock(text='bar')
        b2.save()
        l = Layout()
        l.items.append(b)
        l.items.append(b2)

        html = l.render()

        self.assertEqual(html, '<div class="layout">\n<div class="block">\nfoo\n</div>\n<div class="block">\nbar\n</div>\n</div>')

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

        html = l.render()

        self.assertEqual(html, '<div class="layout">\n<div class="block">\nfoo\n</div>\n<div class="layout">\n<div class="block">\nbar\n</div>\n</div>\n</div>')
