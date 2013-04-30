from mongoengine import StringField
from cms_prototype.models.blocks.block import Block


class Link(Block):
    href = StringField()
    text = StringField()

    meta = {'renderer': '/blocks/link.jade'}
