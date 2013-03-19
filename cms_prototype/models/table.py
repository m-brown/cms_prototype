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
        if not hasattr(self, 'data'):
            populate(self)
        args = {'data': self.data}
        args.update(kwargs)
        return super(MongoTable, self).render(**args)

    def populate(self):
        #TODO - restrict select to the columns
        cursor = MongoTable._get_collection().database[self.collection].find(spec=self.query, sort=self.sort)
        self.data = []
        for row in cursor:
            self.data.append(row)
