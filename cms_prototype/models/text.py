from mongoengine import StringField
from cms_prototype.models.site import Block

class HTMLBlock(Block):

    text = StringField()

    meta = {'renderer': '/blocks/html.mako'}

class MarkdownBlock(HTMLBlock):

    meta = {'renderer': '/blocks/markdown.jade'}
