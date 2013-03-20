from mongoengine import EmbeddedDocument, EmbeddedDocumentField, ReferenceField, StringField, DictField, ListField
from cms_prototype.models.site import Block


class MongoColumn(EmbeddedDocument):
    field = StringField(required=True)
    display = StringField()


class MongoTable(Block):
    database = StringField(required=True)
    collection = StringField(required=True)
    columns = ListField(EmbeddedDocumentField(MongoColumn))
    spec = DictField()
    sort = DictField()

    meta = {'renderer': '/blocks/table.jade'}

    def render(self, **kwargs):
        if not hasattr(self, 'data'):
            self.populate()
        args = {'data': self.data}
        args.update(kwargs)
        return super(MongoTable, self).render(**args)

    def populate(self):
        sort = []
        for key, value in self.sort.iteritems():
            sort.append((key, value))

        fields = {}
        for col in self.columns:
            fields[col.field] = 1

        cursor = MongoTable._get_collection().database[self.collection].find(self.spec, fields=fields, sort=sort)
        self.data = []
        for row in cursor:
            r = {}
            for col in self.columns:
                if not col.field in row:
                    raise AttributeError('The row has not attribute "' + col.field + '"')
                r[col.field] = row[col.field]
            self.data.append(r)
