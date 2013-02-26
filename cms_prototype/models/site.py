from mongoengine import EmbeddedDocumentField, ReferenceField, StringField, DictField, ReferenceField, DENY
from mongoengine import Document, EmbeddedDocument

from cms_prototype.models.base import VersionedDocument

class Site(VersionedDocument):
    name        = StringField()
    unique_name = StringField()

class Page(VersionedDocument):
    handler     = StringField()
    parameters  = DictField()

class UrlKey(EmbeddedDocument):
    site        = ReferenceField('Site', dbref=False)
    url         = StringField()

class Url(EmbeddedDocument):
    key         = EmbeddedDocumentField('UrlKey', primary_key=True)
    page        = ReferenceField(Page)
