from mongoengine import EmbeddedDocumentField, ReferenceField, StringField
from mongoengine import Document, EmbeddedDocument

from cms_prototype.models.base import VersionedDocument

class Site(VersionedDocument):
	name 		= StringField()
	unique_name = StringField()

class UrlKey(EmbeddedDocument):
    url  = StringField()
    site = ReferenceField('Site', dbref=False)

class Url(Document):
    key = EmbeddedDocumentField('UrlKey', primary_key=True)
