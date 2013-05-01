import markdown

from mongoengine import StringField
from cms_prototype.models.blocks.block import Block


class HTMLBlock(Block):

    text = StringField()

    meta = {'renderer': '/blocks/html.jade'}

class MarkdownBlock(HTMLBlock):

    def render(self, **kwargs):
        args = {'text': markdown.markdown(self.text)}
        args.update(kwargs)
        return super(MarkdownBlock, self).render(**args)

