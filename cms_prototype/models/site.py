from cms_prototype.models.base import VersionedDocument

class Site(VersionedDocument):
	name 		= StringField()
	unique_name = StringField() 