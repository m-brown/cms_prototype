from mongoengine import EmbeddedDocumentField, ReferenceField, StringField, DictField, ReferenceField, DENY
from mongoengine import Document, EmbeddedDocument

from cms_prototype.models.base import VersionedDocument

class Block(VersionedDocument):
    name        = StringField()

class Page(VersionedDocument):
    handler     = StringField()
    parameters  = DictField()
    body        = StringField()

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
