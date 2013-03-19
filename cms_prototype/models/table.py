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

    meta = {'renderer': '/blocks/table.mako'}

    def render(self, **kwargs):
        #args = {'rows': .....}
        #args.update(kwargs)
        return super(MongoTable, self).render(**kwargs)

    def populate(self):
        #TODO - restrict select to the columns
        self.cursor = MongoTable._get_collection().database[self.collection].find(spec=self.query, sort=self.sort)
