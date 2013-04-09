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
    	renderer = self._meta.get('renderer')
    	args = {k: v for k, v in self.to_mongo().iteritems() if k[0] != '_'}

        self.html = []
        for item in self.items:
            self.html.append(item.render())
        args['html'] = html

        return render(renderer, args)