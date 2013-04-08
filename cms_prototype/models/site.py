from mongoengine import EmbeddedDocumentField, ReferenceField, StringField, DictField, ListField
from mongoengine import EmbeddedDocument

from pyramid.renderers import render

from cms_prototype.models.base import VersionedDocument, SwitchableTypeField
from cms_prototype.models.blocks.block import Block
from cms_prototype.models.layout import Layout


class Page(VersionedDocument):
    handler     = StringField()
    parameters  = DictField()
    body        = StringField()
    layout      = EmbeddedDocumentField('Layout')


class Site(VersionedDocument):
    name        = StringField()
    unique_name = StringField()
    header      = ReferenceField(Block, dbref=True)
    footer      = ReferenceField(Block, dbref=True)


class UrlKey(EmbeddedDocument):
    site        = ReferenceField('Site', dbref=False)
    url         = StringField()


class Url(VersionedDocument):
    key         = EmbeddedDocumentField('UrlKey', primary_key=True)
    page        = ReferenceField(Page, dbref=True)
