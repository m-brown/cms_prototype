from cms_prototype.models.site import Block
from mongoengine import StringField


class Link(Block):
    href = StringField()
    text = StringField()

    meta = {'renderer': '/blocks/link.jade'}
