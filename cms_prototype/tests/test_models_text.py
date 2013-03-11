from cms_prototype.tests.common import TemplateTestCase

class TextModelsTestCase(TemplateTestCase):

    def test_html_block(self):
        from cms_prototype.models.text import HTMLBlock

        html = '<p>Testing</p>'

        block = HTMLBlock(text=html)
        block.save()

        a = HTMLBlock.objects(id=block.id).first()
        self.assertEqual(a, block)
        self.assertEqual(html, block.render().strip())

    def test_markdown_block(self):
        from cms_prototype.models.text import MarkdownBlock

        html = '<strong>Testing</strong>'
        markdown = '**Testing**'

        block = MarkdownBlock(text=markdown)
        block.save()

        a = MarkdownBlock.objects(id=block.id).first()
        self.assertEqual(a, block)
        self.assertEqual(a.text, markdown)
        self.assertEqual(html, block.render().strip())