from mongoengine import EmbeddedDocumentField, ReferenceField, StringField, DictField, ListField
from mongoengine import EmbeddedDocument

from pyramid.renderers import render

from cms_prototype.models.base import VersionedDocument, SwitchableTypeField
from cms_prototype.models.layout import Layout


class Page(VersionedDocument):
    name           = StringField(required=True)
    handler_module = StringField()
    handler_class  = StringField()
    parameters     = DictField()
    body           = StringField()
    layout         = EmbeddedDocumentField('Layout')


class Site(VersionedDocument):
    name           = StringField(required=True)
    unique_name    = StringField(required=True)
    header         = ReferenceField('Block', dbref=True)
    footer         = ReferenceField('Block', dbref=True)


class Url(VersionedDocument):
    url            = StringField(required=True, unique_with=('site'))
    site           = ReferenceField('Site', dbref=False, required=True)
    page           = ReferenceField('Page', dbref=False, required=True)
