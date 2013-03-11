from mongoengine import BooleanField, IntField, ListField, StringField
from mongoengine import EmbeddedDocument, EmbeddedDocumentField
from cms_prototype.models.site import Block

class Input(EmbeddedDocument):

    type  = StringField(required=True, default='text')
    name  = StringField(required=True)
    label = StringField()

    meta = {'allow_inheritance': True}

class Checkbox(Input):

    def __init__(self, *args, **kwargs):
        kwargs['type'] = 'checkbox'
        super(Checkbox, self).__init__(*args, **kwargs)

    checked = BooleanField(default=False)

class FormBlock(Block):

    type   = IntField(default=1)
    action = StringField(default='', required=False)
    method = StringField(default='POST')
    fields = ListField(EmbeddedDocumentField(Input))

    meta = {'renderer': '/blocks/form.jade'}
