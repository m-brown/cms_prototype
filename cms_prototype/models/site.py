from mongoengine import EmbeddedDocumentField, ReferenceField, StringField, DictField, ListField
from mongoengine import EmbeddedDocument

from pyramid.renderers import render

from cms_prototype.models.base import VersionedDocument, SwitchableTypeField
from cms_prototype.models.layout import Layout


class Page(VersionedDocument):
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


class UrlKey(EmbeddedDocument):
    site           = ReferenceField('Site', dbref=False)
    url            = StringField()


class Url(VersionedDocument):
    key            = EmbeddedDocumentField('UrlKey', primary_key=True)
    page           = ReferenceField('Page', dbref=True)
