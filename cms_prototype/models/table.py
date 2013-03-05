from mongoengine import EmbeddedDocument, ReferenceField, StringField, DictField, ListField
from cms_prototype.models.site import Block


class MongoColumn(EmbeddedDocument):
    field = StringField(required=True)
    display = StringField()


class MongoTable(Block):
    database = StringField(required=True)
    collection = StringField(required=True)
    columns = ListField(MongoColumn)
    query = StringField()
    sort = StringField()

    def populdate(self):
        cursor = MongoTable._get_collection().database[self.collection].find(spec=query, sort=sort)
