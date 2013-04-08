from mongoengine import EmbeddedDocumentField, ReferenceField, StringField, ListField
from mongoengine import EmbeddedDocument

from pyramid.renderers import render
from cms_prototype.models.base import VersionedDocument, SwitchableTypeField
from cms_prototype.models.blocks.block import Block


class Layout(EmbeddedDocument):
    html_id = StringField()
    html_class = StringField()
    items = ListField(SwitchableTypeField((EmbeddedDocumentField('Layout'), ReferenceField(Block, dbref=False))))

    meta = {'renderer': '/layout.jade'}

    def render(self):
        self.html = []
        for item in self.items:
            self.html.append(item.render())
