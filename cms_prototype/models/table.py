from mongoengine import EmbeddedDocumentField, ReferenceField, StringField, DictField
from cms_prototype.models.site import Block


class MongoColumn(EmbeddedDocument):
    field = StringField(require=True)
    display = StringField()


class MongoTable(Block):
    database = StringField(require=True)
    collection = StringField()
    columns = ListField(MongoColumn)
    query = StringField()
    sort = StringField()
